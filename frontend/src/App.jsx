import { useState } from 'react'
import './App.css'

function App() {
  const [prompt, setPrompt] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('http://localhost:8000/api/requirements/extract', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_prompt: prompt }),
      })

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <div className="header">
        <h1>AI Architectural Design Consultant</h1>
        <p>Transform natural language requirements into structured architectural concepts.</p>
      </div>
      
      <div className="input-card">
        <form onSubmit={handleSubmit}>
          <textarea 
            className="prompt-textarea"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="E.g., Design a 3-floor eco-friendly public library for a hot and humid climate with natural ventilation..."
            rows={5}
            required
          />
          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Processing via LLM...' : 'Extract Requirements'}
          </button>
        </form>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error connection to backend:</strong> {error}
        </div>
      )}

      {result && (
        <div className="results-card">
          <h2>Structured Project Requirements</h2>
          
          <div className="result-grid">
            <div className="info-box">
              <span className="info-label">Building Type</span>
              <span className="info-value">{result.building_type}</span>
            </div>
            <div className="info-box">
              <span className="info-label">Climate context</span>
              <span className="info-value">{result.climate}</span>
            </div>
            <div className="info-box">
              <span className="info-label">User Capacity</span>
              <span className="info-value">{result.user_capacity}</span>
            </div>
          </div>
          
          <h3 style={{marginTop: '20px', color: '#334155'}}>Key Design Features</h3>
          <div className="tags-container">
            {result.key_features.map((feature, idx) => (
              <span key={idx} className="tag">{feature}</span>
            ))}
          </div>

          <h3 style={{marginTop: '20px', color: '#334155'}}>Sustainability Goals</h3>
          <div className="tags-container">
            {result.sustainability_goals.map((goal, idx) => (
              <span key={idx} className="tag sustainability-tag">{goal}</span>
            ))}
          </div>
          
          <div className="raw-note">
            <strong>System Note:</strong> {result.raw_extraction}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
