'use client';

import { useState, useRef, useEffect } from 'react';
import JurisdictionToggle from '@/components/JurisdictionToggle';
import './chat.css';

export default function ChatPage() {
  const [jurisdiction, setJurisdiction] = useState('india');
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Namaste! I am IP-SAKTI Sahayak, your AI assistant for Ayurvedic Intellectual Property. Please select your jurisdiction (India or International) and ask me a question.',
      citations: [],
      isGreeting: true
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMessage, jurisdiction })
      });

      if (!response.ok) throw new Error('API request failed');

      const data = await response.json();
      
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || [],
        confidence: data.confidence,
        relatedQueries: data.related_queries || [],
        disclaimer: data.disclaimer
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I apologize, but I encountered an error connecting to the knowledge base. Please ensure the backend server is running.',
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRelatedQueryClick = (query) => {
    setInput(query);
    // Focus the input would be good here
  };

  return (
    <div className="chat-layout">
      <div className="chat-header glass-panel">
        <div className="chat-title">
          <h2>IP Guidance Chat</h2>
          <p>Source-cited answers for Ayurvedic IP</p>
        </div>
        <JurisdictionToggle value={jurisdiction} onChange={setJurisdiction} />
      </div>

      <div className="chat-container glass-panel">
        <div className="messages-area">
          {messages.map((msg, idx) => (
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className="message-content">
                {msg.role === 'assistant' && (
                  <div className="avatar assistant-avatar">S</div>
                )}
                
                <div className={`message-bubble ${msg.isError ? 'error-bubble' : ''}`}>
                  <div className="message-text">
                    {msg.content.split('\n').map((line, i) => (
                      <p key={i}>{line}</p>
                    ))}
                  </div>

                  {msg.citations && msg.citations.length > 0 && (
                    <div className="citations-section">
                      <h4>📜 Sources Cited</h4>
                      <ul className="citation-list">
                        {msg.citations.map((cit, i) => (
                          <li key={i} className="citation-item">
                            <span className="citation-title">{cit.source_title}</span>
                            {cit.section && <span className="citation-section"> — {cit.section}</span>}
                            <span className={`confidence-badge confidence-${cit.confidence?.toLowerCase() || 'medium'}`}>
                              {cit.confidence}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {msg.disclaimer && !msg.isGreeting && (
                    <div className="disclaimer-banner">
                      {msg.disclaimer}
                    </div>
                  )}

                  {msg.relatedQueries && msg.relatedQueries.length > 0 && (
                    <div className="related-queries">
                      <h4>🔗 Related Topics</h4>
                      <div className="query-chips">
                        {msg.relatedQueries.map((query, i) => (
                          <button 
                            key={i} 
                            className="query-chip"
                            onClick={() => handleRelatedQueryClick(query)}
                          >
                            {query}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                {msg.role === 'user' && (
                  <div className="avatar user-avatar">U</div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message-wrapper assistant">
              <div className="message-content">
                <div className="avatar assistant-avatar">S</div>
                <div className="message-bubble typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSubmit} className="input-area">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={`Ask a question about ${jurisdiction === 'india' ? 'Indian' : 'International'} IP law...`}
            className="chat-input"
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
          />
          <button 
            type="submit" 
            className="btn-primary send-btn"
            disabled={!input.trim() || isLoading}
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
      </div>
    </div>
  );
}
