// Service: the only place that talks HTTP to the backend.
async function request(path, options) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

export const fetchMessages = () => request('/messages');

export const postMessage = (content) =>
  request('/messages', { method: 'POST', body: JSON.stringify({ content }) });
