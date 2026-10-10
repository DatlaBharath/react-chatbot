import { useCallback, useEffect, useState } from 'react';
import { toMessage } from '../models/message.js';
import { fetchMessages, postMessage } from '../services/api.js';

// Controller: state + actions the views bind to.
export function useMessages() {
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchMessages()
      .then((rows) => setMessages(rows.map(toMessage)))
      .catch((e) => setError(e.message));
  }, []);

  const send = useCallback(async (content) => {
    try {
      const created = await postMessage(content);
      setMessages((prev) => [...prev, toMessage(created)]);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }, []);

  return { messages, error, send };
}
