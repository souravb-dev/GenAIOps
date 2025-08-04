import React from 'react';

interface TypingIndicatorProps {
  show: boolean;
  message?: string;
}

export function TypingIndicator({ show, message = "AI Assistant is typing..." }: TypingIndicatorProps) {
  if (!show) return null;

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-xs lg:max-w-md bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white rounded-r-lg rounded-tl-lg px-4 py-3 shadow-sm">
        <div className="flex items-center space-x-3">
          {/* Avatar */}
          <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
            <i className="fas fa-robot text-white text-sm"></i>
          </div>
          
          {/* Typing animation */}
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
            <span className="text-sm text-gray-500 dark:text-gray-400 animate-pulse">
              {message}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
} 