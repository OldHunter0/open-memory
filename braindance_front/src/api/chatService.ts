// Chat service API for communicating with the backend
import { getUserId } from '../utils/userIdentifier'
const API_BASE_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;  // Ensure the port is consistent with memoryService

export const chatService = {
    // Send a message to the AI and get a streaming response
    sendMessageStream: async (
        message: string,
        onChunk: (chunk: string) => void,
        onDone: () => void,
        onError: (error: Error) => void
    ): Promise<void> => {
        try {
            const userId = await getUserId();
            console.log(`Sending message to AI (streaming) for user ${userId}:`, message);

            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream',
                },
                body: JSON.stringify({
                    message,
                    user_id: userId
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error("AI response failed:", errorText);
                throw new Error(`Chat request failed: ${response.statusText}`);
            }

            // 处理服务器发送的事件流
            const reader = response.body?.getReader();
            const decoder = new TextDecoder();

            if (!reader) {
                throw new Error("No readable stream available");
            }

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');

                for (const line of lines) {
                    if (line.startsWith('data:')) {
                        try {
                            const data = JSON.parse(line.slice(5).trim());

                            if (data.content) {
                                onChunk(data.content);
                            }

                            if (data.done) {
                                onDone();
                                return;
                            }

                            if (data.error) {
                                throw new Error(data.error);
                            }
                        } catch (parseError) {
                            console.warn("Error parsing SSE data:", parseError);
                        }
                    }
                }
            }

            onDone();
        } catch (error) {
            console.error("Error in streaming chat:", error);
            onError(error instanceof Error ? error : new Error(String(error)));
        }
    },

    // Original non-streaming method as a fallback
    sendMessage: async (message: string): Promise<string> => {
        try {
            const userId = await getUserId();
            console.log(`Sending message to AI for user ${userId}:`, message);

            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message,
                    user_id: userId
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error("AI response failed:", errorText);
                throw new Error(`Chat request failed: ${response.statusText}`);
            }

            const result = await response.json();
            console.log("Received AI response:", result);
            return result.response;
        } catch (error) {
            console.error("Chat request error:", error);
            throw error;
        }
    }
};