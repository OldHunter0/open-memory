import { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { chatService } from '../api/chatService';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';

const ChatContainer = styled(motion.div)`
  background: rgba(10, 10, 10, 0.9);
  border: 1px solid ${({ theme }) => theme.colors.primary};
  border-radius: 8px;
  width: 90%;
  max-width: 1200px;
  height: 70vh;  /* Use viewport height instead of fixed pixel value */
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(5px);
  box-shadow: 0 0 20px rgba(0, 255, 157, 0.2);
  margin: 0 auto;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const MessageBubble = styled.div<{ $isUser: boolean }>`
  background: ${({ $isUser, theme }) =>
    $isUser ? 'rgba(0, 255, 157, 0.1)' : 'rgba(255, 0, 60, 0.1)'};
  border: 1px solid ${({ $isUser, theme }) =>
    $isUser ? theme.colors.primary : theme.colors.secondary};
  padding: 10px 15px;
  border-radius: 12px;
  max-width: 80%;
  align-self: ${({ $isUser }) => ($isUser ? 'flex-end' : 'flex-start')};
  position: relative;
  
  /* Markdown styles */
  & .markdown-content {
    font-family: ${({ theme }) => theme.fonts.secondary};
    color: ${({ theme }) => theme.colors.text};
    
    & p {
      margin: 0.5em 0;
      &:first-child {
        margin-top: 0;
      }
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    & a {
      color: ${({ theme }) => theme.colors.primary};
      text-decoration: none;
      &:hover {
        text-decoration: underline;
      }
    }
    
    & pre {
      background: rgba(0, 0, 0, 0.3);
      border-radius: 4px;
      padding: 8px;
      overflow-x: auto;
    }
    
    & code {
      font-family: monospace;
      background: rgba(0, 0, 0, 0.2);
      padding: 2px 4px;
      border-radius: 3px;
    }
    
    & ul, & ol {
      padding-left: 20px;
      margin: 0.5em 0;
    }
    
    & blockquote {
      border-left: 2px solid ${({ theme }) => theme.colors.primary};
      margin-left: 0;
      margin-right: 0;
      padding-left: 10px;
      color: rgba(255, 255, 255, 0.7);
    }
    
    & img {
      max-width: 100%;
    }
    
    & table {
      border-collapse: collapse;
      width: 100%;
      
      & th, & td {
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 4px 8px;
      }
      
      & th {
        background: rgba(0, 0, 0, 0.2);
      }
    }
  }
`;

const InputContainer = styled.div`
  display: flex;
  padding: 20px;
  gap: 10px;
`;

const InputField = styled.input`
  flex: 1;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid ${({ theme }) => theme.colors.primary};
  padding: 10px;
  color: ${({ theme }) => theme.colors.text};
  font-family: ${({ theme }) => theme.fonts.secondary};
  border-radius: 5px;
`;

const SendButton = styled.button`
  padding: 10px 20px;
  background: rgba(0, 255, 157, 0.2);
  border: 1px solid ${({ theme }) => theme.colors.primary};
  color: ${({ theme }) => theme.colors.text};
  border-radius: 5px;
  cursor: pointer;
  
  &:hover {
    background: rgba(0, 255, 157, 0.3);
  }
`;

// Container for typing indicator
const TypingIndicator = styled.span`
  &::after {
    content: '▋';
    animation: blink 1s infinite;
    margin-left: 2px;
  }
  
  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }
`;

interface Message {
  id: number;
  text: string;
  isUser: boolean;
  isTyping?: boolean;
}

export const ChatWindow = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Automatically scroll to the latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (inputText.trim() && !isLoading) {
      const userMessage: Message = {
        id: Date.now(),
        text: inputText,
        isUser: true,
      };

      // Add user message to chat
      setMessages((prev) => [...prev, userMessage]);

      // Clear input field
      setInputText('');

      // Add AI reply placeholder, initially empty with typing indicator
      const aiMessageId = Date.now() + 1;
      const aiMessage: Message = {
        id: aiMessageId,
        text: '',
        isUser: false,
        isTyping: true
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsLoading(true);

      try {
        // Use streaming API
        await chatService.sendMessageStream(
          userMessage.text,
          // Update message with each received chunk
          (chunk) => {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === aiMessageId
                  ? { ...msg, text: msg.text + chunk }
                  : msg
              )
            );
          },
          // Remove typing indicator when done
          () => {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === aiMessageId
                  ? { ...msg, isTyping: false }
                  : msg
              )
            );
            setIsLoading(false);
          },
          // Error handling
          (error) => {
            setMessages(prev =>
              prev.map(msg =>
                msg.id === aiMessageId
                  ? { ...msg, text: 'Sorry, I am unable to respond to your message. Please try again later.', isTyping: false }
                  : msg
              )
            );
            setIsLoading(false);
          }
        );
      } catch (error) {
        // Fallback: use non-streaming API
        try {
          const aiResponse = await chatService.sendMessage(userMessage.text);
          setMessages((prev) =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, text: aiResponse, isTyping: false }
                : msg
            )
          );
        } catch (fallbackError) {
          setMessages((prev) =>
            prev.map(msg =>
              msg.id === aiMessageId
                ? { ...msg, text: 'Sorry, I am unable to respond to your message. Please try again later.', isTyping: false }
                : msg
            )
          );
        } finally {
          setIsLoading(false);
        }
      }
    }
  };

  // Function to render message content
  const renderMessageContent = (message: Message) => {
    if (message.isUser) {
      // User messages remain as plain text
      return (
        <>
          {message.text}
          {message.isTyping && <TypingIndicator />}
        </>
      );
    } else {
      // AI messages are rendered using Markdown
      return (
        <>
          <div className="markdown-content">
            <ReactMarkdown rehypePlugins={[rehypeRaw]}>
              {message.text}
            </ReactMarkdown>
          </div>
          {message.isTyping && <TypingIndicator />}
        </>
      );
    }
  };

  return (
    <ChatContainer
      initial={{ opacity: 0, y: 50 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <MessagesContainer>
        {messages.map((message) => (
          <MessageBubble key={message.id} $isUser={message.isUser}>
            {renderMessageContent(message)}
          </MessageBubble>
        ))}
        <div ref={messagesEndRef} />
      </MessagesContainer>
      <InputContainer>
        <InputField
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Chat with memory..."
          disabled={isLoading}
        />
        <SendButton onClick={handleSend} disabled={isLoading}>
          {isLoading ? 'SENDING...' : 'SEND'}
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
};