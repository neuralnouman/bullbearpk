export async function submitHybridInput(formData: any, chatMessage: string, userId: string) {
  const res = await fetch('/api/hybrid', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_input: formData, chat_message: chatMessage, user_id: userId }),
  });
  return res.json();
}
