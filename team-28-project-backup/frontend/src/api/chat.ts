import { ChatMessage } from './types';
import { authorizedFetch } from '../utils/authfetch';

// 🟢 Existing functions — KEEP
export const sendMessage = async (message: string): Promise<ChatMessage> => {
  const response = await authorizedFetch('/chat/send', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
  return response.json();
};

export const getChatHistory = async (): Promise<ChatMessage[]> => {
  const response = await authorizedFetch('/chat/history');
  return response.json();
};

// 🔵 NEW function — UPDATED
export const handleChatSubmit = async (text: string, currentUser: any, authToken: string) => {
  try {
    const nlpResponse = await fetch('http://localhost:3000/tasks/nlp', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, user_id: currentUser.uid }),
    });

    const nlpData = await nlpResponse.json();

    // 🔥 ADD THIS: if needsUserInput is true, skip creating event
    if (nlpData.needsUserInput) {
      console.error('NLP extraction incomplete, skipping event creation.');
      return;
    }

    const extracted = nlpData.extracted;

    const createResponse = await fetch('http://localhost:3000/events', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`,
      },
      body: JSON.stringify({
        user_id: currentUser.uid,
        task: extracted.task,
        participants: extracted.participants,
        date: extracted.date,
        time: extracted.time,
        end_time: extracted.end_time,
        locations: extracted.locations,
      }),
    });

    const createdEvent = await createResponse.json();
    console.log('Event created successfully:', createdEvent);

  } catch (error) {
    console.error('Error creating event from chat:', error);
  }
};
