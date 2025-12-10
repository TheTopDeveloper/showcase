'use client';

import { useState, useRef, useEffect, FormEvent } from 'react';
import { Send, Bot, User, Loader2, RefreshCw, Sparkles, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { sendMessage, clearSession, Message } from '@/lib/api';

// UPDATE THESE FOR ACTUAL COMPANY
const COMPANY_NAME = 'NimbusFlow';
const WELCOME_MESSAGE = `Hi! 👋 I'm the ${COMPANY_NAME} support assistant. I can help you with:

• **Pricing & Plans** - Compare options and find the right plan
• **Features** - Learn what's available on each tier
• **Troubleshooting** - Solve common issues quickly
• **Account & Billing** - Manage your subscription
• **General Questions** - Policies, security, and more

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
    "What plans do you offer?",
    "How do I reset my password?",
    "Compare Professional vs Business",
    "Do you have a mobile app?",
  ];

  return (
    <div className="flex flex-col h-screen max-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-semibold text-slate-900">{COMPANY_NAME} Support</h1>
            <p className="text-xs text-slate-500">AI-powered assistant</p>
          </div>
        </div>
        <button onClick={handleClearChat} className="p-2 text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg" title="Clear conversation">
          <RefreshCw className="w-5 h-5" />
        </button>
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto chat-scroll p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className={`flex gap-3 message-enter ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
            )}
            <div className={`max-w-[75%] rounded-2xl px-4 py-3 ${message.role === 'user' ? 'bg-primary-600 text-white' : 'bg-white border border-slate-200 shadow-sm'}`}>
              {message.role === 'assistant' ? (
                <div className="prose-chat"><ReactMarkdown>{message.content}</ReactMarkdown></div>
              ) : (
                <p className="whitespace-pre-wrap">{message.content}</p>
              )}
              {message.sources && message.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-100 flex flex-wrap gap-1">
                  {message.sources.map((source, i) => (
                    <span key={i} className="inline-flex items-center gap-1 text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                      <Sparkles className="w-3 h-3" />{source}
                    </span>
                  ))}
                </div>
              )}
            </div>
            {message.role === 'user' && (
              <div className="flex-shrink-0 w-8 h-8 bg-slate-600 rounded-lg flex items-center justify-center">
                <User className="w-5 h-5 text-white" />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-3 justify-start message-enter">
            <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white border border-slate-200 shadow-sm rounded-2xl px-4 py-3">
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full typing-dot" />
                <div className="w-2 h-2 bg-slate-400 rounded-full typing-dot" />
                <div className="w-2 h-2 bg-slate-400 rounded-full typing-dot" />
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3 message-enter">
            <AlertCircle className="w-5 h-5 flex-shrink-0" /><p className="text-sm">{error}</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions */}
      {messages.length === 1 && (
        <div className="px-4 pb-2">
          <p className="text-xs text-slate-500 mb-2">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion, i) => (
              <button key={i} onClick={() => setInput(suggestion)} className="text-sm bg-white border border-slate-200 hover:border-primary-300 hover:bg-primary-50 px-3 py-1.5 rounded-full transition-colors">
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <div className="border-t border-slate-200 bg-white p-4">
        <form onSubmit={handleSubmit} className="flex gap-3">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question..."
            rows={1}
            className="flex-1 resize-none rounded-xl border border-slate-300 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 px-4 py-3 outline-none"
            disabled={isLoading}
          />
          <button type="submit" disabled={!input.trim() || isLoading} className="w-12 h-12 bg-primary-600 hover:bg-primary-700 disabled:bg-slate-300 text-white rounded-xl flex items-center justify-center">
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
        <p className="text-xs text-slate-400 mt-2 text-center">Press Enter to send • Shift+Enter for new line</p>
      </div>
    </div>
  );
}
