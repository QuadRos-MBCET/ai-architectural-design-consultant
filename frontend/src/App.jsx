import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [prompt, setPrompt] = useState(
    'Design a modern sustainable college library in a tropical hot-humid climate with a reading hall, computer section, discussion rooms, librarian office, storage, toilets, natural ventilation, and solar shading.'
  );
  const [mode, setMode] = useState('rag_consultant'); // 'rag_consultant' or 'experimental_compare'
  const [isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const [consultantData, setConsultantData] = useState(null);
  const [compareData, setCompareData] = useState(null);

  useEffect(() => {
    handleRunPipeline();
  }, []);

  const handleRunPipeline = async () => {
    setIsLoading(true);
    setErrorMsg('');
    setStatusMsg('Running FAISS vector retrieval & architectural RAG pipeline...');

    try {
      if (mode === 'rag_consultant') {
        const res = await fetch(`${API_BASE}/api/consultant/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });

        if (!res.ok) throw new Error(`API returned status ${res.status}`);
        const data = await res.json();
        setConsultantData(data);
        setCompareData(null);
        setStatusMsg('Successfully generated context-aware architectural design consultation & blueprint.');
      } else {
        const res = await fetch(`${API_BASE}/api/consultant/compare`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });

        if (!res.ok) throw new Error(`API returned status ${res.status}`);
        const data = await res.json();
        setCompareData(data);
        setConsultantData(null);
        setStatusMsg('Experimental comparison completed: Standard Prompt-Only vs RAG-Backed Framework.');
      }
    } catch (err) {
      setErrorMsg(`Execution failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadSVG = (svgContent, filename = 'blueprint.svg') => {
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div>
          <h1>AI Architectural Design Consultant</h1>
          <p>A Retrieval-Augmented Generation (RAG) Framework for Context-Aware Conceptual Architectural Design</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Left Controls */}
        <section className="column control-column">
          <div>
            <h2 className="section-title">Architectural Prompt & Site Context</h2>
            <textarea
              className="prompt-input"
              rows={6}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Design a sustainable college library in a tropical climate with reading hall..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Workflow Mode</label>
            <select
              className="select-input"
              value={mode}
              onChange={(e) => setMode(e.target.value)}
            >
              <option value="rag_consultant">RAG Architectural Design Consultant (Our Framework)</option>
              <option value="experimental_compare">Experimental Comparison (Standard vs RAG-Enhanced)</option>
            </select>
          </div>

          <button
            className="btn-primary"
            onClick={handleRunPipeline}
            disabled={isLoading}
          >
            {isLoading ? 'Retrieving Knowledge & Synthesizing...' : 'Run Architectural Analysis'}
          </button>

          {statusMsg && (
            <div className="msg-box msg-success">
              {statusMsg}
            </div>
          )}

          {errorMsg && (
            <div className="msg-box msg-error">
              {errorMsg}
            </div>
          )}
        </section>

        {/* Right Display Area */}
        <section className="column viewer-column">
          {mode === 'rag_consultant' ? (
            consultantData ? (
              <div className="consultant-results-view">
                {/* Knowledge & Strategy Cards */}
                <div className="info-grid">
                  {/* Retrieved Evidence */}
                  <div className="info-card">
                    <h3>FAISS Retrieved Architectural Case Studies</h3>
                    <div className="knowledge-text">
                      {consultantData.retrieved_evidence}
                    </div>
                  </div>

                  {/* Sustainable Climate Strategies */}
                  <div className="info-card">
                    <h3>Sustainable Climate Strategies ({consultantData.climate_zone})</h3>
                    <ul className="strategy-list">
                      {consultantData.passive_strategies.map((strat, idx) => (
                        <li key={idx}>🌿 {strat}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Refined Prompt */}
                  <div className="info-card full-width">
                    <h3>RAG-Refined Context-Aware Diffusion Prompt</h3>
                    <div className="code-text">{consultantData.refined_prompt}</div>
                  </div>
                </div>

                {/* SVG Blueprint Section */}
                <div className="blueprint-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#f0f6fc' }}>Context-Aware 2D Architectural Blueprint</h3>
                      <span className="status-badge badge-success">Suitability Score: {consultantData.suitability_score}%</span>
                    </div>
                    <button className="btn-secondary" onClick={() => downloadSVG(consultantData.floorplan.svg_content || '')}>
                      Download SVG
                    </button>
                  </div>

                  <div className="svg-box" style={{ minHeight: '450px' }}>
                    <div
                      dangerouslySetInnerHTML={{ __html: consultantData.floorplan.svg_content || '' }}
                      style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center' }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="placeholder-box">
                <p>Click "Run Architectural Analysis" to execute RAG retrieval and generate context-aware design guidance.</p>
              </div>
            )
          ) : (
            /* Experimental Comparison Mode */
            compareData && compareData.comparison ? (
              <div className="comparison-view">
                <h2 style={{ fontSize: '1.1rem', margin: '0 0 10px 0', color: '#f0f6fc' }}>
                  Experimental Comparison: Standard Prompt-Only vs RAG-Backed Framework
                </h2>

                <div className="comparison-grid">
                  {/* Baseline Card */}
                  <div className="comparison-card">
                    <div className="card-header">
                      <h3>{compareData.comparison.baseline.name}</h3>
                      <span className="status-badge badge-warning">Standard Baseline</span>
                    </div>
                    <p className="approach-text">{compareData.comparison.baseline.approach}</p>

                    <div className="metric-row">
                      <div><strong>Context-Aware:</strong> ❌ No</div>
                      <div><strong>Climate Rules:</strong> 0</div>
                      <div><strong>Suitability Score:</strong> <span style={{ color: '#d29922' }}>{compareData.comparison.baseline.suitability_score}%</span></div>
                    </div>

                    <div className="svg-box" style={{ height: '320px' }}>
                      <div dangerouslySetInnerHTML={{ __html: compareData.comparison.baseline.svg_content }} style={{ width: '100%', height: '100%' }} />
                    </div>

                    <button className="btn-secondary" onClick={() => downloadSVG(compareData.comparison.baseline.svg_content, 'baseline_floorplan.svg')}>
                      Download Baseline SVG
                    </button>
                  </div>

                  {/* Proposed RAG Card */}
                  <div className="comparison-card highlight-card">
                    <div className="card-header">
                      <h3>{compareData.comparison.proposed_rag.name}</h3>
                      <span className="status-badge badge-success">Proposed RAG Framework</span>
                    </div>
                    <p className="approach-text">{compareData.comparison.proposed_rag.approach}</p>

                    <div className="metric-row">
                      <div><strong>Context-Aware:</strong> ✅ Yes (FAISS RAG)</div>
                      <div><strong>Climate Rules:</strong> {compareData.comparison.proposed_rag.climate_strategies_applied} Applied</div>
                      <div><strong>Suitability Score:</strong> <span style={{ color: '#3fb950' }}>{compareData.comparison.proposed_rag.suitability_score}%</span></div>
                    </div>

                    <div className="svg-box" style={{ height: '320px' }}>
                      <div dangerouslySetInnerHTML={{ __html: compareData.comparison.proposed_rag.svg_content }} style={{ width: '100%', height: '100%' }} />
                    </div>

                    <button className="btn-secondary" onClick={() => downloadSVG(compareData.comparison.proposed_rag.svg_content, 'rag_consultant_floorplan.svg')}>
                      Download RAG Consultant SVG
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="placeholder-box">
                <p>Click "Run Architectural Analysis" to perform experimental comparison between Standard Generation vs RAG-Backed Framework.</p>
              </div>
            )
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
