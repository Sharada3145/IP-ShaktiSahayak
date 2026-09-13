import React from 'react';
import './JurisdictionToggle.css';

export default function JurisdictionToggle({ value, onChange }) {
  return (
    <div className="jurisdiction-toggle-container">
      <div className="toggle-label">Jurisdiction:</div>
      <div className="toggle-wrapper">
        <button
          className={`toggle-btn ${value === 'india' ? 'active-india' : ''}`}
          onClick={() => onChange('india')}
          type="button"
        >
          <span className="flag">🇮🇳</span> India
        </button>
        <button
          className={`toggle-btn ${value === 'international' ? 'active-intl' : ''}`}
          onClick={() => onChange('international')}
          type="button"
        >
          <span className="flag">🌍</span> International
        </button>
      </div>
    </div>
  );
}
