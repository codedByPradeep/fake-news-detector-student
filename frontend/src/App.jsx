import { useState } from 'react';
import './index.css';

function App() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyzeNews = async () => {
    if (!text.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);


    try {
      // Use the Render Backend URL for production, or fallback to localhost for development if needed.
      // Ideally, use an environment variable, but for this student project, we'll hardcode the robust logic.
      const backendUrl = import.meta.env.PROD
        ? 'https://fake-news-detector-student.onrender.com/analyze'
        : 'http://localhost:8000/analyze';

      const response = await fetch(backendUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('Analysis failed. Please try again.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getVerdictClass = (verdict) => {
    if (!verdict) return '';
    return verdict === 'REAL' ? 'result-card REAL' : verdict === 'FAKE' ? 'result-card FAKE' : 'result-card UNKNOWN';
  };

  const getVerdictTextClass = (verdict) => {
    if (!verdict) return '';
    return verdict; // CSS handles .verdict.REAL / .verdict.FAKE
  }

  return (
    <div className="container">
      <header className="app-header">
        <h1>Fake News Detector for Students</h1>
        <p className="subtitle">Analyze articles, assess credibility, and get concise summaries.</p>
      </header>

      <div className="input-group">
        <textarea
          placeholder="Paste the news article text here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={loading}
        />
      </div>

      <button onClick={analyzeNews} disabled={loading || !text.trim()}>
        {loading ? 'Analyzing...' : 'Analyze Article'}
      </button>

      {error && <div className="error-message" style={{ color: 'red', marginTop: '1rem', textAlign: 'center' }}>{error}</div>}

      {result && (
        <div className={`result-card`}>
          <div className="result-header">
            <span style={{ color: 'gray', fontWeight: '600' }}>Verdict:</span>
            <span className={`verdict ${result.result}`}>{result.result}</span>
          </div>

          <div style={{ marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between' }}>
            <span>Confidence Score:</span>
            <strong>{result.confidence}%</strong>
          </div>
          <div className="confidence-bar">
            <div
              className="confidence-fill"
              style={{
                width: `${result.confidence}%`,
                backgroundColor: result.result === 'REAL' ? '#10b981' : result.result === 'FAKE' ? '#ef4444' : '#f59e0b'
              }}
            ></div>
          </div>


          {result.summary && (
            <div className="summary-box">
              <div className="summary-title">Summary</div>
              <p style={{ margin: 0, fontSize: '0.95rem', color: '#4b5563' }}>{result.summary}</p>
            </div>
          )}



          {result.explanation && result.explanation.length > 0 && (
            <div className="explanation-box" style={{ marginBottom: '1.5rem' }}>
              <div className="summary-title">Key Indicators</div>
              <div className="features-list">
                {result.explanation.map((word, index) => (
                  <span key={index} className="feature-tag">#{word}</span>
                ))}
              </div>
            </div>
          )}

          {result.live_verification && result.live_verification.status !== 'UNVERIFIED' && (
            <div className="summary-box" style={{ backgroundColor: result.live_verification.status === 'VERIFIED_REAL' ? '#f0fdf4' : '#fef2f2', border: result.live_verification.status === 'VERIFIED_REAL' ? '1px solid #bbf7d0' : '1px solid #fecaca' }}>
              <div className="summary-title" style={{ color: result.live_verification.status === 'VERIFIED_REAL' ? '#15803d' : '#b91c1c' }}>
                {result.live_verification.status === 'VERIFIED_REAL' ? '✅ Verified by Reliable Sources' : '⚠️ No Reliable Sources Found'}
              </div>
              <p style={{ margin: 0, fontSize: '0.95rem', color: '#4b5563' }}>
                {result.live_verification.message}
              </p>
              {result.live_verification.sources.length > 0 && result.live_verification.status === 'VERIFIED_REAL' && (
                <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', marginBottom: 0, fontSize: '0.9rem' }}>
                  {result.live_verification.sources.filter(s => s.is_reliable).slice(0, 3).map((source, i) => (
                    <li key={i}><a href={source.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'underline' }}>{source.title}</a> (via {source.domain})</li>
                  ))}
                </ul>
              )}
            </div>
          )}

        </div>
      )}
    </div>
  );
}

export default App;
