import React, { useState, useRef, useEffect } from 'react';
import { chatbotApi } from '../services/api';

const quickQuestions = [
  "Why is my bill high?",
  "How can I save energy?",
  "What's my usage today?",
  "Tell me about my AC",
  "Predict tomorrow's usage",
  "Show recommendations",
];

export default function ChatPage({ t, language, selectedHome }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef(null);

  const fetchHistory = async () => {
    // Start with a fresh welcome message every time. No database history loaded.
    setMessages([
      {
        id: 'welcome',
        role: 'bot',
        message: `Hello! 👋 I'm your Vidhyuth Netra AI assistant. I can help you understand your energy usage, explain your bill, suggest ways to save, and answer questions about your devices. What would you like to know about ${selectedHome.name}?`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  useEffect(() => {
    fetchHistory();
  }, [selectedHome]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async (text) => {
    const msg = text || input.trim();
    if (!msg || !selectedHome) return;
    setInput('');

    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      message: msg,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const result = await chatbotApi.query(selectedHome.id, msg);
      if (result && result.response) {
        const botMsg = {
          id: `bot-${Date.now()}`,
          role: 'bot',
          message: result.response,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };
        setMessages(prev => [...prev, botMsg]);
      }
    } catch (err) {
      console.error("Chat query failed:", err);
      const errorMsg = {
        id: `error-${Date.now()}`,
        role: 'bot',
        message: "Sorry, I encountered an issue querying my energy database. Please try again.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  };

  return (
    <div>
      <div className="page-header">
        <h1>🤖 Chat Assistant</h1>
        <p>Ask me anything about your home energy usage</p>
      </div>

      {/* Quick Questions */}
      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 20 }}>
        {quickQuestions.map(q => (
          <button
            key={q}
            className="command-chip"
            onClick={() => sendMessage(q)}
            style={{ cursor: 'pointer' }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat Window */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid var(--border)',
          display: 'flex', alignItems: 'center', gap: 10
        }}>
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, var(--teal), var(--blue))',
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18
          }}>🤖</div>
          <div>
            <div style={{ fontSize: 14, fontWeight: 600 }}>Vidhyuth AI</div>
            <div style={{ fontSize: 11, color: 'var(--green)', display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--green)', display: 'inline-block' }}></span>
              Online · Knows your home data
            </div>
          </div>
        </div>

        <div style={{ padding: 20 }}>
          <div className="chat-container">
            <div className="chat-messages">
              {messages.map(msg => (
                <div key={msg.id} className={`chat-bubble ${msg.role === 'user' ? 'user' : ''}`}>
                  <div className={`chat-avatar ${msg.role === 'user' ? 'user' : ''}`}>
                    {msg.role === 'user' ? '👤' : '🤖'}
                  </div>
                  <div>
                    <div className="chat-text">{msg.message}</div>
                    <div className="chat-time">{msg.time}</div>
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="chat-bubble">
                  <div className="chat-avatar">🤖</div>
                  <div>
                    <div className="chat-text" style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
                      <span style={{ display: 'inline-flex', gap: 3 }}>
                        {[0, 1, 2].map(i => (
                          <span key={i} style={{
                            width: 7, height: 7, borderRadius: '50%',
                            background: 'var(--teal)',
                            animation: 'pulse 1.2s ease infinite',
                            animationDelay: `${i * 0.2}s`,
                            display: 'inline-block'
                          }}></span>
                        ))}
                      </span>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 4 }}>Thinking…</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            <div className="chat-input-row">
              <input
                className="chat-input"
                placeholder="Ask about your energy usage, devices, bill..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
              />
              <button className="chat-send" onClick={() => sendMessage()}>➤</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
