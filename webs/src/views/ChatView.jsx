import { useState } from 'react';
import { useMessages } from '../controllers/useMessages.js';

export default function ChatView() {
  const { messages, error, send } = useMessages();
  const [draft, setDraft] = useState('');

  const onSubmit = (e) => {
    e.preventDefault();
    const text = draft.trim();
    if (!text) return;
    send(text);
    setDraft('');
  };

  return (
    <main style={{ maxWidth: 640, margin: '2rem auto', fontFamily: 'sans-serif' }}>
      <h1>Chatbot</h1>
      {error && <p role="alert">{error}</p>}
      <ul>
        {messages.map((m) => (
          <li key={m.id}>{m.content}</li>
        ))}
      </ul>
      <form onSubmit={onSubmit}>
        <input
          aria-label="message"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Type a message"
        />
        <button type="submit">Send</button>
      </form>
    </main>
  );
}
