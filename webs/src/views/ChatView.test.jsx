import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import ChatView from './ChatView.jsx';

const row = (id, content) => ({ id, role: 'user', content, created_at: '2025-01-01T00:00:00' });

beforeEach(() => {
  global.fetch = vi.fn(async (url, opts) => {
    if (opts?.method === 'POST') {
      return { ok: true, json: async () => row(2, JSON.parse(opts.body).content) };
    }
    return { ok: true, json: async () => [row(1, 'first')] };
  });
});

afterEach(() => vi.restoreAllMocks());

test('loads and shows existing messages', async () => {
  render(<ChatView />);
  expect(await screen.findByText('first')).toBeInTheDocument();
});

test('sends a new message', async () => {
  render(<ChatView />);
  await screen.findByText('first');
  await userEvent.type(screen.getByLabelText('message'), 'hello');
  await userEvent.click(screen.getByRole('button', { name: 'Send' }));
  expect(await screen.findByText('hello')).toBeInTheDocument();
});
