from typing import Any, List, Mapping, Optional, Sequence
from uuid import uuid4

import requests
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.utils.function_calling import convert_to_openai_tool

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _convert_tool_to_gemini(tool_like: Any) -> dict[str, Any]:
    oai_function = convert_to_openai_tool(tool_like)["function"]
    declaration: dict[str, Any] = {
        "name": oai_function["name"],
        "description": oai_function.get("description", ""),
    }
    parameters = oai_function.get("parameters")
    if parameters:
        declaration["parameters"] = parameters
    return declaration


def _messages_to_gemini_payload(messages: List[BaseMessage]) -> dict[str, Any]:
    system_texts: List[str] = []
    contents: List[dict[str, Any]] = []

    for message in messages:
        if isinstance(message, SystemMessage):
            system_texts.append(message.content)
        elif isinstance(message, HumanMessage):
            contents.append({"role": "user", "parts": [{"text": message.content}]})
        elif isinstance(message, AIMessage):
            parts: List[dict[str, Any]] = []
            if message.content:
                parts.append({"text": message.content})
            for tool_call in message.tool_calls:
                call = {"name": tool_call["name"], "args": tool_call["args"]}
                parts.append({"functionCall": call})
            contents.append({"role": "model", "parts": parts})
        elif isinstance(message, ToolMessage):
            contents.append(
                {
                    "role": "user",
                    "parts": [
                        {
                            "functionResponse": {
                                "name": message.name,
                                "response": {"result": message.content},
                            }
                        }
                    ],
                }
            )
        else:
            raise ValueError(f"Unsupported message type for Gemini chat: {type(message)}")

    payload: dict[str, Any] = {"contents": contents}
    if system_texts:
        payload["systemInstruction"] = {"parts": [{"text": "\n".join(system_texts)}]}
    return payload


class GemmaLLM(BaseChatModel):
    """LangChain chat model wrapper around the Gemini API for a Gemma model (LangGraph nodes)."""

    model: str = ""
    api_key: str = ""
    temperature: float = 0.7
    max_output_tokens: int = 1024

    @property
    def _llm_type(self) -> str:
        return "gemma-chat"

    def bind_tools(
        self,
        tools: Sequence[Any],
        *,
        tool_choice: Optional[str] = None,
        **kwargs: Any,
    ) -> Runnable[Any, AIMessage]:
        formatted_tools = [_convert_tool_to_gemini(t) for t in tools]

        tool_config = None
        if tool_choice is not None:
            if tool_choice in ("auto", "any", "none"):
                mode = tool_choice.upper()
                tool_config = {"functionCallingConfig": {"mode": mode}}
            else:
                tool_config = {
                    "functionCallingConfig": {"mode": "ANY", "allowedFunctionNames": [tool_choice]}
                }

        bind_kwargs: dict[str, Any] = {"tools": formatted_tools}
        if tool_config is not None:
            bind_kwargs["tool_config"] = tool_config

        return self.bind(**bind_kwargs, **kwargs)

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        tools: Optional[List[dict[str, Any]]] = None,
        tool_config: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        if not self.model:
            raise ValueError("GEMINI_MODEL is not set")

        generation_config: dict[str, Any] = {
            "temperature": self.temperature,
            "maxOutputTokens": self.max_output_tokens,
        }
        if stop:
            generation_config["stopSequences"] = stop

        payload = _messages_to_gemini_payload(messages)
        payload["generationConfig"] = generation_config
        if tools:
            payload["tools"] = [{"functionDeclarations": tools}]
        if tool_config:
            payload["toolConfig"] = tool_config

        response = requests.post(
            GEMINI_API_URL.format(model=self.model),
            params={"key": self.api_key},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()

        try:
            parts = data["candidates"][0]["content"]["parts"]
        except (KeyError, IndexError) as exc:
            raise ValueError(f"Unexpected Gemini response shape: {data}") from exc

        text_parts: List[str] = []
        tool_calls: List[dict[str, Any]] = []
        for part in parts:
            if part.get("thought"):
                continue
            if "functionCall" in part:
                function_call = part["functionCall"]
                tool_calls.append(
                    {
                        "name": function_call["name"],
                        "args": function_call.get("args", {}),
                        "id": f"call_{uuid4().hex[:24]}",
                        "type": "tool_call",
                    }
                )
            elif "text" in part:
                text_parts.append(part["text"])

        message = AIMessage(content="".join(text_parts), tool_calls=tool_calls)
        return ChatResult(generations=[ChatGeneration(message=message)])

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model": self.model, "temperature": self.temperature}
