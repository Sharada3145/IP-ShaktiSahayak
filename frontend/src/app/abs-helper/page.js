'use client';

import { useState } from 'react';
import './abs.css';

export default function ABSHelperPage() {
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const startAssessment = async () => {
    setIsLoading(true);
    setMessages([]);
    setResult(null);
    try {
      const res = await fetch('/api/tools/abs-check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      const data = await res.json();
      handleResponse(data);
    } catch (error) {
      console.error('Failed to start ABS check', error);
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async (answerText) => {
    if (isLoading || !sessionId) return;
    
    // Add user answer to chat
    setMessages(prev => [...prev, { role: 'user', content: answerText }]);
    setIsLoading(true);
    
    try {
      const res = await fetch('/api/tools/abs-check/followup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, response: answerText })
      });
      const data = await res.json();
      handleResponse(data);
    } catch (error) {
      console.error('Failed to submit answer', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResponse = (data) => {
    setSessionId(data.session_id);
    
    if (data.is_complete) {
      setResult(data);
    } else {
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: data.message,
          options: data.options 
        }
      ]);
    }
  };

  return (
    <div className="abs-layout">
      <div className="abs-header glass-panel">
        <h2>ABS Compliance Helper</h2>
        <p>Navigate the Biological Diversity Act requirements based on your specific profile and intended use.</p>
      </div>

      <div className="abs-content">
        <div className="wizard-panel glass-panel">
          {messages.length === 0 && !result ? (
            <div className="initial-state">
              <div className="icon-large bg-green">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
                </svg>
              </div>
              <h3>Start Compliance Assessment</h3>
              <p>We'll ask a few questions to determine whether you need prior intimation to the State Biodiversity Board, prior approval from the National Biodiversity Authority, or if you fall under an exemption.</p>
              <button onClick={startAssessment} className="btn-primary" disabled={isLoading}>
                {isLoading ? 'Starting...' : 'Start Assessment'}
              </button>
            </div>
          ) : (
            <div className="conversation-state">
              <div className="wizard-messages">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`wizard-msg ${msg.role}`}>
                    <p>{msg.content}</p>
                    
                    {msg.role === 'assistant' && msg.options && (
                      <div className="options-container">
                        {msg.options.map((opt, i) => (
                          <button 
                            key={i}
                            className="btn-secondary option-btn"
                            onClick={() => submitAnswer(opt)}
                            disabled={isLoading}
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                
                {isLoading && (
                  <div className="wizard-msg assistant typing">
                    <span></span><span></span><span></span>
                  </div>
                )}
              </div>
              
              {result && (
                <button onClick={startAssessment} className="btn-secondary restart-btn mt-4">
                  Start New Assessment
                </button>
              )}
            </div>
          )}
        </div>

        {result && (
          <div className="results-panel glass-panel animate-fade-in">
            <div className="result-header">
              <h3>Assessment Result</h3>
              <div className={`status-badge ${result.is_exempt ? 'status-exempt' : 'status-required'}`}>
                {result.is_exempt ? 'Exempt' : 'Compliance Required'}
              </div>
            </div>
            
            <div className="result-section">
              <h4>Requirement</h4>
              <p className="highlight-text">{result.requirement}</p>
            </div>
            
            <div className="result-section">
              <h4>Forms Required</h4>
              {result.forms_required && result.forms_required.length > 0 ? (
                <ul>
                  {result.forms_required.map((form, i) => (
                    <li key={i}>{form}</li>
                  ))}
                </ul>
              ) : (
                <p>No forms required based on your profile.</p>
              )}
            </div>
            
            <div className="result-section">
              <h4>Benefit Sharing</h4>
              <p>{result.benefit_sharing}</p>
            </div>
            
            <div className="result-section summary-section">
              <h4>Summary</h4>
              <p>{result.summary}</p>
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
