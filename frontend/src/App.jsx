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
    <div className="App" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <h1>AI Architectural Design Consultant</h1>
      <p>Enter your architectural requirements below to get started.</p>
      
      <form onSubmit={handleSubmit}>
        <textarea 
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="E.g., Design a 3-floor eco-friendly public library for a hot and humid climate..."
          rows={6}
          style={{ width: '100%', padding: '10px', marginBottom: '10px' }}
          required
        />
        <br />
        <button type="submit" disabled={loading} style={{ padding: '10px 20px', fontSize: '16px' }}>
          {loading ? 'Processing...' : 'Extract Requirements'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'red', marginTop: '20px' }}>
          <strong>Error:</strong> {error}
        </div>
      )}

      {result && (
        <div style={{ marginTop: '30px', textAlign: 'left', background: '#f4f4f4', padding: '20px', borderRadius: '5px' }}>
          <h2>Extracted Requirements</h2>
          <p><strong>Building Type:</strong> {result.building_type}</p>
          <p><strong>Climate:</strong> {result.climate}</p>
          <p><strong>User Capacity:</strong> {result.user_capacity}</p>
          
          <h3>Key Features</h3>
          <ul>
            {result.key_features.map((feature, idx) => (
              <li key={idx}>{feature}</li>
            ))}
          </ul>

          <h3>Sustainability Goals</h3>
          <ul>
            {result.sustainability_goals.map((goal, idx) => (
              <li key={idx}>{goal}</li>
            ))}
          </ul>
          
          <div style={{ marginTop: '20px', padding: '10px', background: '#e0e0e0', fontSize: '0.9em' }}>
            <strong>Raw LLM Note:</strong> {result.raw_extraction}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
