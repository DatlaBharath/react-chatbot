// Model: shape of a message as the UI uses it.
export function toMessage(raw) {
  return {
    id: raw.id,
    role: raw.role,
    content: raw.content,
    createdAt: new Date(raw.created_at),
  };
}
