'use client';

import { useState, useRef, useEffect, FormEvent } from 'react';
import { Send, Bot, User, Loader2, RefreshCw, Sparkles, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendMessage, clearSession, Message } from '@/lib/api';

const COMPANY_NAME = 'TechStore Pro';
const WELCOME_MESSAGE = `Hi! 👋 I'm the ${COMPANY_NAME} support assistant. I can help you with:

• **Product Search** - Find monitors, printers, and computer accessories
• **Product Details** - Get specifications, pricing, and availability
• **Order Management** - Check order status and place new orders
• **Customer Support** - Answer questions about products and orders
• **Product Recommendations** - Find the right products for your needs

How can I help you today?`;

function generateId(): string {
  return Math.random().toString(36).substring(2, 15);
}

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([
    { id: 'welcome', role: 'assistant', content: WELCOME_MESSAGE, timestamp: new Date() },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const trimmedInput = input.trim();
    if (!trimmedInput || isLoading) return;

    setError(null);
    setInput('');

    const userMessage: Message = {
      id: generateId(),
      role: 'user',
      content: trimmedInput,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await sendMessage(trimmedInput, sessionId || undefined);
      if (!sessionId) setSessionId(response.session_id);

      const assistantMessage: Message = {
        id: generateId(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(response.timestamp),
        sources: response.sources_used,
        tools: response.tools_called,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
      setMessages(prev => prev.filter(m => m.id !== userMessage.id));
      setInput(trimmedInput);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = async () => {
    if (sessionId) {
      try { await clearSession(sessionId); } catch {}
    }
    setSessionId(null);
    setMessages([{ id: 'welcome', role: 'assistant', content: WELCOME_MESSAGE, timestamp: new Date() }]);
    setError(null);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as FormEvent);
    }
  };

  const suggestions = [
    "What monitors do you have?",
    "Show me printers under $300",
    "I need a 4K monitor",
    "Check my order status",
  ];

  return (
    <div className="flex flex-col h-full bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
      {/* Header */}
      <header className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 px-4 py-3 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30">
            <Bot className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-white text-sm">{COMPANY_NAME} Support</h1>
            <p className="text-xs text-blue-100">AI-powered assistant</p>
          </div>
        </div>
        <button onClick={handleClearChat} className="p-1.5 text-white/80 hover:text-white hover:bg-white/20 rounded-lg transition-colors" title="Clear conversation">
          <RefreshCw className="w-4 h-4" />
        </button>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto chat-scroll p-3 md:p-4 space-y-3 bg-gradient-to-b from-slate-50 to-white">
        {messages.map((message) => (
          <div key={message.id} className={`flex gap-2.5 message-enter ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center shadow-sm">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}
            <div className={`max-w-[80%] rounded-xl px-3 py-2 text-sm ${message.role === 'user' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md' : 'bg-white border border-slate-200 shadow-sm'}`}>
              {message.role === 'assistant' ? (
                <div className="prose-chat text-sm"><ReactMarkdown>{message.content}</ReactMarkdown></div>
              ) : (
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{message.content}</p>
              )}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-1.5 pt-1.5 border-t border-slate-100 flex flex-wrap gap-1">
                  {message.sources.map((source, i) => (
                    <span key={i} className="inline-flex items-center gap-1 text-xs bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 px-2 py-0.5 rounded-full border border-blue-200">
                      <Sparkles className="w-2.5 h-2.5" />{source}
                    </span>
                  ))}
                </div>
              )}
            </div>
            {message.role === 'user' && (
              <div className="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center shadow-sm">
                <User className="w-4 h-4 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-2.5 justify-start message-enter">
            <div className="flex-shrink-0 w-7 h-7 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center shadow-sm">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-white border border-slate-200 shadow-sm rounded-xl px-3 py-2">
              <div className="flex items-center gap-1">
                <div className="w-1.5 h-1.5 bg-blue-400 rounded-full typing-dot" />
                <div className="w-1.5 h-1.5 bg-indigo-400 rounded-full typing-dot" />
                <div className="w-1.5 h-1.5 bg-purple-400 rounded-full typing-dot" />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2 message-enter text-sm">
            <AlertCircle className="w-4 h-4 flex-shrink-0" /><p>{error}</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length === 1 && (
        <div className="px-3 md:px-4 pb-2">
          <p className="text-xs text-slate-500 mb-1.5 font-medium">Try asking:</p>
          <div className="flex flex-wrap gap-1.5">
            {suggestions.map((suggestion, i) => (
              <button key={i} onClick={() => setInput(suggestion)} className="text-xs bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 hover:border-blue-400 hover:from-blue-100 hover:to-indigo-100 text-blue-700 px-2.5 py-1 rounded-full transition-all shadow-sm">
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-slate-200 bg-gradient-to-r from-white to-slate-50 p-3 md:p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question..."
            rows={1}
            className="flex-1 resize-none rounded-lg border border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 px-3 py-2 text-sm outline-none transition-all"
            disabled={isLoading}
          />
          <button type="submit" disabled={!input.trim() || isLoading} className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:from-slate-300 disabled:to-slate-400 text-white rounded-lg flex items-center justify-center shadow-md transition-all disabled:shadow-none">
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </form>
        <p className="text-xs text-slate-400 mt-1.5 text-center">Press Enter to send • Shift+Enter for new line</p>
      </div>
    </div>
  );
}
