'use client';

import { useState } from 'react';
import './classify.css';

export default function ClassifyPage() {
  const [description, setDescription] = useState('');
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [result, setResult] = useState(null);

  const startClassification = async (e) => {
    e.preventDefault();
    if (!description.trim() || isLoading) return;

    const initialDesc = description.trim();
    setDescription('');
    setIsLoading(true);
    setMessages([{ role: 'user', content: initialDesc }]);
    
    try {
      const res = await fetch('/api/tools/classify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: initialDesc })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      handleResponse(data);
    } catch (error) {
      console.error('Classification error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'An error occurred while connecting to the classifier service. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFollowup = async (e) => {
    e.preventDefault();
    if (!description.trim() || isLoading || !sessionId) return;

    const userResponse = description.trim();
    setDescription('');
    setMessages(prev => [...prev, { role: 'user', content: userResponse }]);
    setIsLoading(true);

    try {
      const res = await fetch('/api/tools/classify/followup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ response: userResponse, session_id: sessionId })
      });
      
      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      handleResponse(data);
    } catch (error) {
      console.error('Followup error:', error);
      setMessages(prev => [...prev, { role: 'assistant', content: 'An error occurred during follow-up. Please try again.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResponse = (data) => {
    if (data.session_id) {
      setSessionId(data.session_id);
    }
    
    if (data.is_complete) {
      setIsComplete(true);
      setResult(data);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Classification complete! Your product falls under: ${data.category_label || data.category}` 
      }]);
    } else {
      setMessages(prev => [...prev, { role: 'assistant', content: data.message }]);
    }
  };

  const resetWizard = () => {
    setDescription('');
    setMessages([]);
    setSessionId(null);
    setIsComplete(false);
    setResult(null);
  };

  return (
    <div className="classify-layout">
      <div className="classify-header glass-panel">
        <h2>Formulation Classifier</h2>
        <p>Determine the regulatory pathway and IP implications for your Ayurvedic product.</p>
      </div>

      <div className="classify-content">
        <div className="wizard-panel glass-panel">
          {messages.length === 0 ? (
            <div className="initial-state">
              <div className="icon-large bg-blue">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
              </div>
              <h3>Describe Your Formulation</h3>
              <p>Tell us about your product's ingredients, preparation method, and intended use to begin.</p>
              
              <form onSubmit={startClassification} className="initial-form">
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="E.g., A polyherbal formulation containing Ashwagandha and Brahmi extracts, intended to reduce stress, sold under a brand name..."
                  rows={4}
                  className="classify-input"
                  required
                />
                <button type="submit" className="btn-primary" disabled={isLoading || !description.trim()}>
                  {isLoading ? 'Analyzing...' : 'Start Classification'}
                </button>
              </form>
            </div>
          ) : (
            <div className="conversation-state">
              <div className="wizard-messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`wizard-msg ${msg.role}`}>
                    {msg.content}
                  </div>
                ))}
                
                {isLoading && (
                  <div className="wizard-msg assistant typing">
                    <span></span><span></span><span></span>
                  </div>
                )}
              </div>
              
              {!isComplete && (
                <form onSubmit={handleFollowup} className="followup-form">
                  <input
                    type="text"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Answer the question(s) above..."
                    className="classify-input-small"
                    disabled={isLoading}
                  />
                  <button type="submit" className="btn-primary small-btn" disabled={isLoading || !description.trim()}>
                    Reply
                  </button>
                </form>
              )}
              
              {isComplete && (
                <button onClick={resetWizard} className="btn-secondary restart-btn">
                  Classify Another Product
                </button>
              )}
            </div>
          )}
        </div>

        {isComplete && result && (
          <div className="results-panel glass-panel animate-fade-in">
            <div className="result-header">
              <h3>Classification Result</h3>
              <div className="category-badge">{result.category_label}</div>
            </div>
            
            <div className="result-section">
              <h4>Regulatory Requirements</h4>
              <ul>
                {result.regulatory_requirements?.map((req, i) => (
                  <li key={i}>{req}</li>
                ))}
              </ul>
            </div>
            
            <div className="result-section">
              <h4>Intellectual Property Implications</h4>
              <ul>
                {result.ip_implications?.map((ip, i) => (
                  <li key={i}>{ip}</li>
                ))}
              </ul>
            </div>
            
            <div className="result-section">
              <h4>Access & Benefit Sharing (ABS)</h4>
              <p className="abs-text">{result.abs_implications}</p>
            </div>
            
            <div className="result-section">
              <h4>Relevant Statutes</h4>
              <div className="statute-tags">
                {result.relevant_statutes?.map((statute, i) => (
                  <span key={i} className="statute-tag">{statute}</span>
                ))}
              </div>
            </div>
            
            <div className="disclaimer-banner mt-4">
              {result.disclaimer}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
