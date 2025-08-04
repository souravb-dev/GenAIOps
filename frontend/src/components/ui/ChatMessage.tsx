import React, { useState } from 'react';
import { ChatMessage as ChatMessageType, IntentResponse, TemplateResponse } from '../../types/chatbot';
import { chatbotService } from '../../services/chatbotService';

interface ChatMessageProps {
  message: ChatMessageType;
  onFeedback?: (rating: number, feedback?: string) => void;
  onTemplateSelect?: (template: TemplateResponse) => void;
  onRetry?: () => void;
}

export function ChatMessage({ message, onFeedback, onTemplateSelect, onRetry }: ChatMessageProps) {
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackText, setFeedbackText] = useState('');
  const [showTemplates, setShowTemplates] = useState(false);

  const handleFeedbackSubmit = () => {
    if (onFeedback && feedbackRating > 0) {
      onFeedback(feedbackRating, feedbackText);
      setShowFeedback(false);
      setFeedbackRating(0);
      setFeedbackText('');
    }
  };

  const renderContent = () => {
    if (message.isLoading) {
      return (
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          </div>
          <span className="text-sm text-gray-500">Thinking...</span>
        </div>
      );
    }

    return (
      <div 
        className="prose prose-sm max-w-none"
        dangerouslySetInnerHTML={{ 
          __html: chatbotService.parseMarkdown(message.content) 
        }}
      />
    );
  };

  const renderIntent = (intent: IntentResponse) => {
    const iconClass = chatbotService.getIntentIcon(intent.intent_type);
    const colorClass = chatbotService.getIntentColor(intent.intent_type);
    
    return (
      <div className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${colorClass} mb-2`}>
        <i className={`${iconClass} mr-1`}></i>
        <span className="capitalize">
          {intent.intent_type.replace('_', ' ')}
        </span>
        <span className="ml-1 opacity-75">
          ({Math.round(intent.confidence_score * 100)}%)
        </span>
      </div>
    );
  };

  const renderOCIInsights = (insights: Record<string, any>) => {
    if (!insights || Object.keys(insights).length === 0) return null;

    return (
      <div className="mt-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
        <div className="flex items-center mb-2">
          <i className="fas fa-cloud text-blue-500 mr-2"></i>
          <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
            OCI Insights
          </span>
        </div>
        
        {insights.compartment && (
          <div className="text-sm text-gray-600 dark:text-gray-300 mb-1">
            <strong>Compartment:</strong> {insights.compartment.name || insights.compartment.id}
          </div>
        )}
        
        {insights.alerts && insights.alerts.length > 0 && (
          <div className="text-sm text-gray-600 dark:text-gray-300">
            <strong>Active Alerts:</strong> {insights.alerts.length}
            {insights.alerts.slice(0, 2).map((alert: any, index: number) => (
              <div key={index} className="ml-2 text-xs opacity-75">
                • {alert.name || 'Alert'} ({alert.severity || 'Unknown'})
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderSuggestedTemplates = (templates: TemplateResponse[]) => {
    if (!templates || templates.length === 0) return null;

    return (
      <div className="mt-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            Suggested Templates
          </span>
          <button
            onClick={() => setShowTemplates(!showTemplates)}
            className="text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400"
          >
            {showTemplates ? 'Hide' : 'Show'} ({templates.length})
          </button>
        </div>
        
        {showTemplates && (
          <div className="space-y-2">
            {templates.slice(0, 3).map((template) => (
              <button
                key={template.id}
                onClick={() => onTemplateSelect?.(template)}
                className="w-full text-left p-2 text-sm bg-gray-50 dark:bg-gray-800 rounded border hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div className="font-medium text-gray-900 dark:text-white">
                  {template.name}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {template.description}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    );
  };

  const renderMessageActions = () => {
    if (message.isUser || message.isLoading) return null;

    return (
      <div className="flex items-center mt-2 space-x-2">
        {/* Feedback button */}
        <button
          onClick={() => setShowFeedback(!showFeedback)}
          className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
          title="Rate this response"
        >
          <i className="fas fa-thumbs-up mr-1"></i>
          Feedback
        </button>

        {/* Copy button */}
        <button
          onClick={() => navigator.clipboard.writeText(message.content)}
          className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
          title="Copy message"
        >
          <i className="fas fa-copy mr-1"></i>
          Copy
        </button>

        {/* Retry button */}
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-xs text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
            title="Regenerate response"
          >
            <i className="fas fa-redo mr-1"></i>
            Retry
          </button>
        )}

        {/* Model info */}
        {message.model_used && (
          <span className="text-xs text-gray-400 dark:text-gray-500">
            {message.model_used} • {message.tokens_used} tokens
            {message.response_time && ` • ${message.response_time.toFixed(2)}s`}
            {message.cached && ' • cached'}
          </span>
        )}
      </div>
    );
  };

  const renderFeedbackForm = () => {
    if (!showFeedback) return null;

    return (
      <div className="mt-3 p-3 bg-gray-50 dark:bg-gray-800 rounded-lg border">
        <div className="mb-3">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Rate this response:
          </label>
          <div className="flex space-x-1">
            {[1, 2, 3, 4, 5].map((rating) => (
              <button
                key={rating}
                onClick={() => setFeedbackRating(rating)}
                className={`w-6 h-6 rounded ${
                  rating <= feedbackRating
                    ? 'text-yellow-400'
                    : 'text-gray-300 hover:text-yellow-400'
                } transition-colors`}
              >
                <i className="fas fa-star"></i>
              </button>
            ))}
          </div>
        </div>

        <div className="mb-3">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Additional feedback (optional):
          </label>
          <textarea
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            className="w-full px-2 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            rows={2}
            placeholder="Tell us how we can improve..."
          />
        </div>

        <div className="flex space-x-2">
          <button
            onClick={handleFeedbackSubmit}
            disabled={feedbackRating === 0}
            className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Submit
          </button>
          <button
            onClick={() => {
              setShowFeedback(false);
              setFeedbackRating(0);
              setFeedbackText('');
            }}
            className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Cancel
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className={`flex ${message.isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg ${
          message.isUser
            ? 'bg-blue-500 text-white rounded-l-lg rounded-tr-lg'
            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-r-lg rounded-tl-lg'
        } px-4 py-3 shadow-sm`}
      >
        {/* Intent indicator for assistant messages */}
        {!message.isUser && message.intent && renderIntent(message.intent)}

        {/* Message content */}
        <div className="mb-2">
          {renderContent()}
        </div>

        {/* OCI Insights */}
        {!message.isUser && message.oci_insights && renderOCIInsights(message.oci_insights)}

        {/* Suggested templates */}
        {!message.isUser && message.suggested_templates && renderSuggestedTemplates(message.suggested_templates)}

        {/* Timestamp */}
        <div className={`text-xs mt-2 ${
          message.isUser ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
        }`}>
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>

        {/* Message actions */}
        {renderMessageActions()}

        {/* Feedback form */}
        {renderFeedbackForm()}
      </div>
    </div>
  );
} 