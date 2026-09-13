'use client';

import { useEffect, useState } from 'react';
import './page.css';

export default function Home() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className={`landing-container ${mounted ? 'animate-fade-in' : 'opacity-0'}`}>
      <div className="hero-section">
        <h1 className="hero-title">
          Navigate Ayurvedic <span className="highlight-gradient">Intellectual Property</span> with Confidence
        </h1>
        <p className="hero-subtitle">
          An AI-powered legal assistant providing authoritative, source-cited guidance across national and international IP regimes, regulatory pathways, and ABS compliance.
        </p>
        
        <div className="hero-actions">
          <a href="/chat" className="btn-primary hero-btn">
            Ask an IP Question
            <svg className="icon-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </a>
          <a href="/classify" className="btn-secondary hero-btn">
            Classify My Formulation
          </a>
        </div>
      </div>
      
      <div className="features-grid">
        <div className="feature-card glass-panel">
          <div className="feature-icon bg-saffron">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="16" x2="12" y2="12"></line>
              <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
          </div>
          <h3>Jurisdiction-Aware Answers</h3>
          <p>Strict separation between Indian national law and International treaties to ensure accurate, context-specific guidance.</p>
        </div>
        
        <div className="feature-card glass-panel">
          <div className="feature-icon bg-green">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
            </svg>
          </div>
          <h3>Source-Cited Authority</h3>
          <p>Every answer is grounded in a curated corpus of statutes, rules, and treaties, complete with confidence indicators and exact citations.</p>
        </div>
        
        <div className="feature-card glass-panel">
          <div className="feature-icon bg-blue">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
              <line x1="12" y1="22.08" x2="12" y2="12"></line>
            </svg>
          </div>
          <h3>Formulation Classification</h3>
          <p>An intelligent wizard that maps your Ayurvedic product to its correct regulatory pathway and outlines IP implications.</p>
        </div>
      </div>
    </div>
  );
}
