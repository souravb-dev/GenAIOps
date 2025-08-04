import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage } from '../ui/ChatMessage';
import { TypingIndicator } from '../ui/TypingIndicator';
import { TemplateSelector } from '../ui/TemplateSelector';
import { ConversationHistory } from '../ui/ConversationHistory';
import { ChatAnalytics } from '../ui/ChatAnalytics';
import {
  ChatMessage as ChatMessageType,
  EnhancedChatRequest,
  TemplateResponse,
  SuggestedQueriesResponse,
  ConversationResponse,
  ConversationWithMessagesResponse
} from '../../types/chatbot';
import { chatbotService } from '../../services/chatbotService';

interface ChatbotPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ChatbotPanel({ isOpen, onClose }: ChatbotPanelProps) {
  // State management
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [conversation, setConversation] = useState<ConversationResponse | null>(null);
  const [showTemplateSelector, setShowTemplateSelector] = useState(false);
  const [showConversationHistory, setShowConversationHistory] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [suggestedQueries, setSuggestedQueries] = useState<SuggestedQueriesResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isMinimized, setIsMinimized] = useState(false);

  // Refs for accessibility
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Initialize
  useEffect(() => {
    if (isOpen && !sessionId) {
      initializeChat();
    }
  }, [isOpen]);

  // Auto-scroll to bottom
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Accessibility: Focus management
  useEffect(() => {
    if (isOpen && !isMinimized) {
      // Focus input when panel opens
      setTimeout(() => {
        inputRef.current?.focus();
      }, 300);
    }
  }, [isOpen, isMinimized]);

  // Accessibility: Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      // ESC to close
      if (e.key === 'Escape') {
        onClose();
      }

      // Ctrl/Cmd + / to focus input
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        inputRef.current?.focus();
      }

      // Ctrl/Cmd + H to open history
      if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
        e.preventDefault();
        setShowConversationHistory(true);
      }

      // Ctrl/Cmd + T to open templates
      if ((e.ctrlKey || e.metaKey) && e.key === 't') {
        e.preventDefault();
        setShowTemplateSelector(true);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const initializeChat = async () => {
    try {
      // Generate session ID
      const newSessionId = chatbotService.generateSessionId();
      setSessionId(newSessionId);

      // Load suggested queries
      const queries = await chatbotService.getSuggestedQueries();
      setSuggestedQueries(queries);

      // Add welcome message
      const welcomeMessage: ChatMessageType = {
        id: 0,
        conversation_id: 0,
        role: 'assistant' as any,
        content: "👋 Hello! I'm your GenAI CloudOps assistant. I can help you with infrastructure queries, troubleshooting, cost optimization, and more. How can I assist you today?",
        model_used: 'system',
        tokens_used: 0,
        response_time: 0,
        cached: false,
        created_at: new Date().toISOString(),
        isUser: false,
        timestamp: new Date()
      };

      setMessages([welcomeMessage]);
      setError(null);
    } catch (err) {
      console.error('Failed to initialize chat:', err);
      setError('Failed to initialize chat. Please try again.');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async (message?: string, templateVariables?: Record<string, any>) => {
    const messageText = message || inputMessage.trim();
    if (!messageText && !templateVariables) return;

    setIsLoading(true);
    setError(null);

    try {
      // Add user message
      const userMessage: ChatMessageType = {
        id: messages.length + 1,
        conversation_id: conversation?.id || 0,
        role: 'user' as any,
        content: messageText,
        tokens_used: 0,
        cached: false,
        created_at: new Date().toISOString(),
        isUser: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, userMessage]);
      setInputMessage('');

      // Prepare enhanced chat request
      const chatRequest: EnhancedChatRequest = {
        message: messageText,
        session_id: sessionId,
        context: templateVariables || {},
        enable_intent_recognition: true,
        use_templates: true
      };

      // Get OCI context if needed (placeholder for now)
      // In a real implementation, this would come from current context
      const ociContext = {
        // compartment_id: currentCompartment?.id,
        // user_id: currentUser?.id
      };

      if (Object.keys(ociContext).length > 0) {
        chatRequest.oci_context = ociContext;
      }

      // Send to backend
      const response = await chatbotService.sendMessage(chatRequest);

      // Create conversation if first message
      if (!conversation && response.conversation_id) {
        try {
          const newConversation = await chatbotService.createConversation({
            title: chatbotService.formatConversationTitle(messageText)
          });
          setConversation(newConversation);
        } catch (convErr) {
          console.warn('Failed to create conversation record:', convErr);
        }
      }

      // Add AI response
      const aiMessage: ChatMessageType = {
        id: messages.length + 2,
        conversation_id: response.conversation_id || 0,
        role: 'assistant' as any,
        content: response.response,
        model_used: response.model,
        tokens_used: response.tokens_used,
        response_time: response.response_time,
        cached: response.cached,
        created_at: new Date().toISOString(),
        isUser: false,
        timestamp: new Date(),
        intent: response.intent,
        suggested_templates: response.suggested_templates,
        oci_insights: response.oci_insights
      };

      setMessages(prev => [...prev, aiMessage]);

      // Announce new message to screen readers
      if (response.response) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = `AI Assistant responded: ${response.response.substring(0, 100)}${response.response.length > 100 ? '...' : ''}`;
        document.body.appendChild(announcement);
        setTimeout(() => document.body.removeChild(announcement), 1000);
      }

    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message
      const errorMessage: ChatMessageType = {
        id: messages.length + 2,
        conversation_id: 0,
        role: 'assistant' as any,
        content: "I'm sorry, I encountered an error processing your request. Please try again or contact support if the issue persists.",
        tokens_used: 0,
        cached: false,
        created_at: new Date().toISOString(),
        isUser: false,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleTemplateSelect = (template: TemplateResponse, variables?: Record<string, any>) => {
    const formattedMessage = variables 
      ? chatbotService.formatTemplateText(template.template_text, variables)
      : template.template_text;
    
    sendMessage(formattedMessage, variables);
    setShowTemplateSelector(false);
  };

  const handleConversationSelect = (conversationData: ConversationWithMessagesResponse) => {
    // Load the selected conversation
    setConversation(conversationData.conversation);
    setSessionId(conversationData.conversation.session_id);
    
    // Convert messages to ChatMessageType format
    const convertedMessages: ChatMessageType[] = conversationData.messages.map(msg => ({
      ...msg,
      isUser: msg.role === 'user',
      timestamp: new Date(msg.created_at)
    }));
    
    setMessages(convertedMessages);
    setShowConversationHistory(false);
  };

  const handleFeedback = async (messageId: number, rating: number, feedbackText?: string) => {
    try {
      await chatbotService.submitFeedback({
        session_id: sessionId,
        message_id: messageId,
        rating,
        feedback_text: feedbackText
      });
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  };

  const handleRetry = () => {
    // Get the last user message and resend it
    const lastUserMessage = [...messages].reverse().find(msg => msg.isUser);
    if (lastUserMessage) {
      sendMessage(lastUserMessage.content);
    }
  };

  const handleExportConversation = async (format: 'json' | 'csv' | 'markdown' = 'markdown') => {
    if (!sessionId) return;

    try {
      const exportData = await chatbotService.exportConversation(sessionId, {
        session_id: sessionId,
        format,
        include_metadata: true
      });

      chatbotService.downloadExport(exportData);
    } catch (err) {
      console.error('Failed to export conversation:', err);
      setError('Failed to export conversation');
    }
  };

  const renderQuickActions = () => {
    if (!suggestedQueries) return null;

    const allQueries = [
      ...suggestedQueries.infrastructure_queries.slice(0, 2),
      ...suggestedQueries.monitoring_queries.slice(0, 2),
      ...suggestedQueries.troubleshooting_queries.slice(0, 1),
      ...suggestedQueries.cost_queries.slice(0, 1)
    ];

    return (
      <div className="flex flex-wrap gap-2 mb-3" role="group" aria-label="Quick action buttons">
        {allQueries.map((query, index) => (
          <button
            key={index}
            onClick={() => sendMessage(query)}
            className="px-3 py-1 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
            title={query}
            aria-label={`Quick action: ${query}`}
          >
            {query.length > 40 ? `${query.substring(0, 40)}...` : query}
          </button>
        ))}
      </div>
    );
  };

  const renderChatHeader = () => (
    <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700 bg-blue-50 dark:bg-blue-900">
      <div className="flex items-center">
        <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center mr-3" aria-hidden="true">
          <i className="fas fa-robot text-white text-sm"></i>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
            AI Assistant
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {conversation?.title || 'CloudOps Helper'}
          </p>
        </div>
      </div>
      
      <div className="flex items-center space-x-2" role="toolbar" aria-label="Chat actions">
        {/* Analytics button */}
        <button
          onClick={() => setShowAnalytics(true)}
          className="p-1 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          title="View analytics (Ctrl+A)"
          aria-label="View conversation analytics"
        >
          <i className="fas fa-chart-bar text-sm"></i>
        </button>

        {/* History button */}
        <button
          onClick={() => setShowConversationHistory(true)}
          className="p-1 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          title="View conversation history (Ctrl+H)"
          aria-label="View conversation history"
        >
          <i className="fas fa-history text-sm"></i>
        </button>

        {/* Export button */}
        <button
          onClick={() => handleExportConversation()}
          className="p-1 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          title="Export conversation"
          aria-label="Export current conversation"
        >
          <i className="fas fa-download text-sm"></i>
        </button>

        {/* Template button */}
        <button
          onClick={() => setShowTemplateSelector(true)}
          className="p-1 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          title="Use template (Ctrl+T)"
          aria-label="Select a query template"
        >
          <i className="fas fa-magic text-sm"></i>
        </button>

        {/* Minimize button */}
        <button
          onClick={() => setIsMinimized(!isMinimized)}
          className="p-1 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          title={isMinimized ? "Restore chat window" : "Minimize chat window"}
          aria-label={isMinimized ? "Restore chat window" : "Minimize chat window"}
        >
          <i className={`fas ${isMinimized ? 'fa-window-restore' : 'fa-window-minimize'} text-sm`}></i>
        </button>

        {/* Close button */}
        <button
          onClick={onClose}
          className="p-1 rounded-md text-gray-400 hover:text-gray-500 dark:hover:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
          title="Close chat (Esc)"
          aria-label="Close chat window"
        >
          <i className="fas fa-times text-lg"></i>
        </button>
      </div>
    </div>
  );

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop for mobile */}
      <div
        className="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 md:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Chatbot Panel */}
      <div
        className={`fixed inset-y-0 right-0 z-50 w-96 bg-white dark:bg-gray-800 shadow-xl transform transition-all duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        } ${isMinimized ? 'h-16' : 'h-full'}`}
        style={{ 
          height: isMinimized ? '64px' : '100vh',
          overflow: isMinimized ? 'hidden' : 'auto'
        }}
        role="dialog"
        aria-label="AI Assistant Chat"
        aria-modal="true"
      >
        <div className="flex flex-col h-full">
          
          {/* Header */}
          {renderChatHeader()}

          {!isMinimized && (
            <>
              {/* Error message */}
              {error && (
                <div className="mx-4 mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm" role="alert">
                  {error}
                  <button
                    onClick={() => setError(null)}
                    className="float-right text-red-500 hover:text-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                    aria-label="Dismiss error message"
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              )}

              {/* Messages */}
              <div 
                ref={messagesContainerRef}
                className="flex-1 overflow-y-auto p-4 space-y-2"
                role="log"
                aria-label="Conversation messages"
                aria-live="polite"
                aria-atomic="false"
              >
                {messages.map((message) => (
                  <ChatMessage
                    key={message.id}
                    message={message}
                    onFeedback={(rating, feedback) => handleFeedback(message.id, rating, feedback)}
                    onTemplateSelect={handleTemplateSelect}
                    onRetry={message.isUser ? undefined : handleRetry}
                  />
                ))}
                
                <TypingIndicator show={isLoading} />
                <div ref={messagesEndRef} aria-hidden="true" />
              </div>

              {/* Input area */}
              <div className="border-t border-gray-200 dark:border-gray-700 p-4">
                {/* Quick actions */}
                {renderQuickActions()}

                {/* Main input */}
                <div className="flex space-x-2">
                  <div className="flex-1">
                    <label htmlFor="chat-input" className="sr-only">
                      Type your message
                    </label>
                    <textarea
                      id="chat-input"
                      ref={inputRef}
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Ask about resources, metrics, or get help... (Ctrl+/ to focus)"
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                      rows={2}
                      disabled={isLoading}
                      aria-describedby="chat-input-help"
                    />
                    <div id="chat-input-help" className="sr-only">
                      Press Enter to send, Shift+Enter for new line. Use keyboard shortcuts: Ctrl+T for templates, Ctrl+H for history.
                    </div>
                  </div>
                  <button
                    onClick={() => sendMessage()}
                    disabled={!inputMessage.trim() || isLoading}
                    className="px-3 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
                    aria-label={isLoading ? "Sending message..." : "Send message"}
                  >
                    <i className={`fas ${isLoading ? 'fa-spinner fa-spin' : 'fa-paper-plane'} text-sm`} aria-hidden="true"></i>
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Modals */}
      <TemplateSelector
        isOpen={showTemplateSelector}
        onClose={() => setShowTemplateSelector(false)}
        onTemplateSelect={handleTemplateSelect}
      />

      <ConversationHistory
        isOpen={showConversationHistory}
        onClose={() => setShowConversationHistory(false)}
        onConversationSelect={handleConversationSelect}
      />

      <ChatAnalytics
        isOpen={showAnalytics}
        onClose={() => setShowAnalytics(false)}
      />
    </>
  );
} 