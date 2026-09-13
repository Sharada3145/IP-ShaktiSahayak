'use client';

import { useState } from 'react';
import './tkdl.css';

export default function TKDLCheckPage() {
  const [ingredients, setIngredients] = useState('');
  const [indication, setIndication] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!ingredients.trim() || !indication.trim() || isLoading) return;

    setIsLoading(true);
    setResult(null);

    // Split ingredients by comma
    const parsedIngredients = ingredients.split(',').map(i => i.trim()).filter(i => i.length > 0);

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/tools/tkdl-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients: parsedIngredients, indication })
      });
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error('Failed to run TKDL check', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="tkdl-layout">
      <div className="tkdl-header glass-panel">
        <h2>TKDL Prior-Art Pointer</h2>
        <p>Check if your Ayurvedic formulation ingredients and intended use face potential Section 3(p) objections based on known traditional knowledge.</p>
      </div>

      <div className="tkdl-content">
        <div className="input-panel glass-panel">
          <h3>Formulation Details</h3>
          <p className="text-muted mb-4">Enter the botanicals and the primary indication (e.g., "Turmeric, Neem" for "Wound Healing").</p>
          
          <form onSubmit={handleCheck} className="tkdl-form">
            <div className="form-group">
              <label>Botanical Ingredients (comma separated)</label>
              <textarea
                value={ingredients}
                onChange={(e) => setIngredients(e.target.value)}
                placeholder="E.g., Curcuma longa, Azadirachta indica, Ashwagandha"
                rows={3}
                required
                className="tkdl-input"
              />
            </div>
            
            <div className="form-group">
              <label>Primary Therapeutic Indication</label>
              <input
                type="text"
                value={indication}
                onChange={(e) => setIndication(e.target.value)}
                placeholder="E.g., Skin infection, stress relief, memory enhancement"
                required
                className="tkdl-input"
              />
            </div>

            <button type="submit" className="btn-primary mt-2" disabled={isLoading || !ingredients || !indication}>
              {isLoading ? 'Checking TK Database...' : 'Run Prior-Art Check'}
            </button>
          </form>
        </div>

        <div className="results-panel glass-panel">
          {result ? (
            <div className="animate-fade-in">
              <div className="result-header">
                <h3>Analysis Results</h3>
                <div className={`risk-badge risk-${result.section_3p_risk.toLowerCase().replace('/', '-')}`}>
                  Risk Level: {result.section_3p_risk}
                </div>
              </div>

              <div className="findings-list">
                <h4>Ingredient Analysis ({result.ingredients_analyzed} identified)</h4>
                {result.findings.map((finding, idx) => (
                  <div key={idx} className="finding-card">
                    <div className="finding-title">
                      <strong>{finding.ingredient}</strong>
                      <span className={`match-status status-${finding.match_status.toLowerCase().replace(/[^a-z]/g, '')}`}>
                        {finding.match_status}
                      </span>
                    </div>
                    <p className="finding-desc">{finding.description}</p>
                    {finding.known_indications && (
                      <div className="known-uses">
                        <small>Known Uses: {finding.known_indications.join(', ')}</small>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="advice-section">
                <h4>Strategic IP Advice</h4>
                <p>{result.strategic_advice}</p>
              </div>

              <div className="disclaimer-banner mt-4">
                {result.disclaimer}
              </div>
            </div>
          ) : (
            <div className="empty-state">
              <div className="icon-large bg-saffron">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <circle cx="10" cy="13" r="2"></circle>
                  <line x1="11.4" y1="14.4" x2="15" y2="18"></line>
                </svg>
              </div>
              <p>Submit your formulation details to run a simulated prior-art check against known traditional knowledge records.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
