import './globals.css';

export const metadata = {
  title: 'IP-SAKTI Sahayak | Ayurveda IP Assistant',
  description: 'A multilingual, RAG-based AI assistant for Intellectual Property and regulatory guidance in Ayurveda.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <div className="app-container">
          <header className="app-header">
            <a href="/" className="logo-container">
              <div className="logo-icon">S</div>
              <div className="logo-text">IP-SAKTI <span className="logo-highlight">Sahayak</span></div>
            </a>
            <nav className="nav-links">
              <a href="/chat" className="nav-link">Ask Question</a>
              <a href="/classify" className="nav-link">Classify Formulation</a>
              <a href="/abs-helper" className="nav-link">ABS Compliance</a>
              <a href="/tkdl-check" className="nav-link">TKDL Check</a>
            </nav>
          </header>
          
          <main className="main-content">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
