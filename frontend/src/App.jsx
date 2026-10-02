import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [prompt, setPrompt] = useState(
    'Create a modern college library of 30m x 20m with a reading hall, computer section, two discussion rooms, librarian office, storage and toilets.'
  );
  const [selectedModel, setSelectedModel] = useState('compare_3'); // 'compare_3', 'gan', 'vae', 'diffusion', 'bsp_baseline'
  
  const [isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const [singleResult, setSingleResult] = useState(null);
  const [compareResult, setCompareResult] = useState(null);

  // Initial generation on load
  useEffect(() => {
    handleGenerate();
  }, []);

  const handleGenerate = async () => {
    setIsLoading(true);
    setErrorMsg('');
    setStatusMsg('Parsing prompt and synthesizing 2D floor plans...');

    try {
      if (selectedModel === 'compare_3') {
        const res = await fetch(`${API_BASE}/api/floorplan/compare`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: prompt })
        });

        if (!res.ok) throw new Error(`API returned status ${res.status}`);
        const data = await res.json();
        setCompareResult(data);
        setSingleResult(null);
        setStatusMsg('Successfully generated 2D layouts across GAN, VAE, and Diffusion models.');
      } else {
        const res = await fetch(`${API_BASE}/api/floorplan/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: prompt,
            model: selectedModel
          })
        });

        if (!res.ok) throw new Error(`API returned status ${res.status}`);
        const data = await res.json();
        setSingleResult(data);
        setCompareResult(null);
        setStatusMsg(`Generated 2D layout using ${selectedModel.toUpperCase()}.`);
      }
    } catch (err) {
      setErrorMsg(`Generation failed: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const downloadSVG = (svgContent, filename = 'floorplan.svg') => {
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
      {/* Header Bar */}
      <header className="app-header">
        <div>
          <h1>2D Architectural Floor Plan Generator</h1>
          <p>Demonstrating 3 Generative AI Architectures: Conditional GAN, Conditional VAE & DDPM Diffusion</p>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Left Control Column */}
        <section className="column control-column">
          <div>
            <h2 className="section-title">Natural Language Prompt</h2>
            <textarea
              className="prompt-input"
              rows={5}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Create a college library with reading hall, computer section, librarian office, storage and toilets..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Model Selection</label>
            <select
              className="select-input"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              <option value="compare_3">Compare All 3 AI Models (GAN vs VAE vs Diffusion)</option>
              <option value="gan">1. Conditional GAN (PyTorch Checkpoint)</option>
              <option value="vae">2. Conditional VAE (PyTorch Checkpoint)</option>
              <option value="diffusion">3. Conditional DDPM Diffusion (PyTorch Checkpoint)</option>
              <option value="bsp_baseline">4. BSP Baseline (Procedural Benchmark)</option>
            </select>
          </div>

          <button
            className="btn-primary"
            onClick={handleGenerate}
            disabled={isLoading}
          >
            {isLoading ? 'Generating Layouts...' : 'Generate 2D Floor Plan'}
          </button>

          {statusMsg && (
            <div style={{ fontSize: '0.82rem', color: '#3fb950', backgroundColor: 'rgba(35,134,54,0.1)', padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(55,185,80,0.2)' }}>
              {statusMsg}
            </div>
          )}

          {errorMsg && (
            <div style={{ fontSize: '0.82rem', color: '#f85149', backgroundColor: 'rgba(248,81,73,0.1)', padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(248,81,73,0.2)' }}>
              {errorMsg}
            </div>
          )}
        </section>

        {/* Right Display Column */}
        <section className="column viewer-column">
          {/* Comparison View (GAN vs VAE vs Diffusion) */}
          {compareResult && compareResult.comparison ? (
            <div className="comparison-grid">
              {['gan', 'vae', 'diffusion'].map((mKey) => {
                const mData = compareResult.comparison[mKey];
                if (!mData) return null;
                return (
                  <div key={mKey} className="comparison-card">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <h3 style={{ margin: 0, fontSize: '1.0rem', color: '#f0f6fc' }}>{mData.model_name}</h3>
                      <span className="status-badge badge-success">
                        Trained Checkpoint
                      </span>
                    </div>

                    <div className="svg-box">
                      <div dangerouslySetInnerHTML={{ __html: mData.svg_content }} style={{ width: '100%', height: '100%' }} />
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.82rem', color: '#8b949e' }}>
                      <span><strong>Rooms:</strong> {mData.floorplan.rooms.length}</span>
                      <span><strong>Latency:</strong> {mData.generation_time_ms} ms</span>
                      <button className="btn-secondary" style={{ width: 'auto', padding: '4px 10px' }} onClick={() => downloadSVG(mData.svg_content, `${mKey}_floorplan.svg`)}>
                        Download SVG
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : singleResult && singleResult.floorplan ? (
            /* Single Model View */
            <div className="single-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <h2 style={{ margin: 0, fontSize: '1.1rem', color: '#f0f6fc' }}>
                  {singleResult.actual_model_used.toUpperCase()} Generated 2D Blueprint
                </h2>
                <button className="btn-secondary" style={{ width: 'auto', padding: '6px 14px' }} onClick={() => downloadSVG(singleResult.svg_content, `${singleResult.actual_model_used}_floorplan.svg`)}>
                  Download SVG
                </button>
              </div>

              <div className="svg-box" style={{ flex: 1, minHeight: '520px' }}>
                <div dangerouslySetInnerHTML={{ __html: singleResult.svg_content }} style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center' }} />
              </div>
            </div>
          ) : (
            <div className="svg-display-card">
              <p style={{ color: '#8b949e' }}>Click "Generate 2D Floor Plan" to synthesize layouts for GAN, VAE, and Diffusion models.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
