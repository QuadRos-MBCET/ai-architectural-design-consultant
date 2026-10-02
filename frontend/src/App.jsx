import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [prompt, setPrompt] = useState(
    'Create a modern college library of 30m × 20m with a large reading hall, computer section, two discussion rooms, librarian office, storage and toilets.'
  );
  const [buildingType, setBuildingType] = useState('library');
  const [width, setWidth] = useState(30);
  const [length, setLength] = useState(20);
  const [selectedModel, setSelectedModel] = useState('gan');
  
  const [viewMode, setViewMode] = useState('single'); // 'single' or 'compare'
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
    setStatusMsg('Parsing requirements & executing generative model...');

    try {
      if (viewMode === 'single') {
        const res = await fetch(`${API_BASE}/api/floorplan/generate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: prompt,
            model: selectedModel,
            building_type: buildingType,
            width: Number(width),
            length: Number(length)
          })
        });

        if (!res.ok) throw new Error(`API returned status ${res.status}`);
        const data = await res.json();
        setSingleResult(data);
        setStatusMsg(data.status);
      } else {
        const res = await fetch(`${API_BASE}/api/floorplan/compare`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: prompt,
            building_type: buildingType,
            width: Number(width),
            length: Number(length)
          })
        });

        if (!res.ok) throw new Error(`API returned status ${res.status}`);
        const data = await res.json();
        setCompareResult(data);
        setStatusMsg('Comparative analysis completed for VAE, GAN, and BSP Baseline.');
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

  const downloadPNG = (svgContent, filename = 'floorplan.png') => {
    const img = new Image();
    const svgBlob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      const canvas = document.createElement('canvas');
      canvas.width = img.width || 800;
      canvas.height = img.height || 600;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0);
      URL.revokeObjectURL(url);

      const a = document.createElement('a');
      a.href = canvas.toDataURL('image/png');
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    };
    img.src = url;
  };

  return (
    <div className="app-container">
      {/* Header Bar */}
      <header className="app-header">
        <div>
          <h1>Prompt-Based 2D Floor Plan Generator</h1>
          <p>Generative Architectural Layout Synthesis using Conditional GAN, VAE & DDPM Diffusion Models</p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            className={`btn-secondary ${viewMode === 'single' ? 'active' : ''}`}
            onClick={() => { setViewMode('single'); }}
            style={{ backgroundColor: viewMode === 'single' ? '#238636' : '#21262d', color: '#fff' }}
          >
            Single Model Mode
          </button>
          <button
            className={`btn-secondary ${viewMode === 'compare' ? 'active' : ''}`}
            onClick={() => { setViewMode('compare'); }}
            style={{ backgroundColor: viewMode === 'compare' ? '#238636' : '#21262d', color: '#fff' }}
          >
            Compare Models (GAN vs VAE vs Diffusion vs BSP)
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Left Control Column */}
        <section className="column control-column">
          <div>
            <h2 className="section-title">Describe Your Floor Plan</h2>
            <textarea
              className="prompt-input"
              rows={6}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. Create a modern college library of 30m × 20m with a large reading hall..."
            />
          </div>

          <div className="form-group">
            <label className="form-label">Building Typology</label>
            <select
              className="select-input"
              value={buildingType}
              onChange={(e) => setBuildingType(e.target.value)}
            >
              <option value="library">College Library</option>
              <option value="hospital">Healthcare Clinic / Hospital</option>
              <option value="mall">Shopping Mall / Retail</option>
              <option value="office">Corporate Office</option>
              <option value="school">Educational School</option>
              <option value="house">Residential House / Villa</option>
              <option value="museum">Public Museum</option>
              <option value="warehouse">Industrial Warehouse</option>
            </select>
          </div>

          <div className="dimension-row">
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Width (Meters)</label>
              <input
                type="number"
                className="number-input"
                min="10"
                max="100"
                value={width}
                onChange={(e) => setWidth(e.target.value)}
              />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label className="form-label">Length (Meters)</label>
              <input
                type="number"
                className="number-input"
                min="10"
                max="100"
                value={length}
                onChange={(e) => setLength(e.target.value)}
              />
            </div>
          </div>

          {viewMode === 'single' && (
            <div className="form-group">
              <label className="form-label">Generative AI Model</label>
              <select
                className="select-input"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                <option value="gan">Conditional GAN (PyTorch Checkpoint)</option>
                <option value="vae">Conditional VAE (PyTorch Checkpoint)</option>
                <option value="diffusion">Conditional DDPM Diffusion (PyTorch Checkpoint)</option>
                <option value="bsp_baseline">BSP Baseline (Procedural Benchmark)</option>
              </select>
            </div>
          )}

          <button
            className="btn-primary"
            onClick={handleGenerate}
            disabled={isLoading}
          >
            {isLoading ? 'Generating Floor Plan...' : 'Generate 2D Floor Plan'}
          </button>

          {statusMsg && (
            <div style={{ fontSize: '0.82rem', color: '#58a6ff', backgroundColor: 'rgba(56,139,253,0.1)', padding: '8px 12px', borderRadius: '6px', border: '1px solid rgba(56,139,253,0.2)' }}>
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
          {viewMode === 'single' ? (
            singleResult && singleResult.floorplan ? (
              <>
                {/* SVG Blueprint Viewer */}
                <div className="svg-display-card">
                  <div
                    dangerouslySetInnerHTML={{ __html: singleResult.svg_content }}
                    style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center' }}
                  />
                </div>

                {/* Metrics & Validation Panel */}
                <div className="metrics-panel">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ margin: 0, fontSize: '1.0rem', color: '#f0f6fc' }}>Generation Summary & Metrics</h3>
                      <span className={`status-badge ${singleResult.is_trained_checkpoint ? 'badge-success' : 'badge-warning'}`} style={{ marginTop: '4px' }}>
                        {singleResult.is_trained_checkpoint ? 'Trained Checkpoint Output' : 'Development Fallback'}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button className="btn-secondary" onClick={() => downloadSVG(singleResult.svg_content)}>
                        Download SVG
                      </button>
                      <button className="btn-secondary" onClick={() => downloadPNG(singleResult.svg_content)}>
                        Download PNG
                      </button>
                      <button className="btn-primary" onClick={handleGenerate}>
                        Regenerate
                      </button>
                    </div>
                  </div>

                  <div className="metrics-grid">
                    <div className="metric-card">
                      <div className="val">{singleResult.actual_model_used.toUpperCase()}</div>
                      <div className="lbl">Model Architecture</div>
                    </div>
                    <div className="metric-card">
                      <div className="val">{singleResult.floorplan.building_width}m × {singleResult.floorplan.building_length}m</div>
                      <div className="lbl">Boundary Dimensions</div>
                    </div>
                    <div className="metric-card">
                      <div className="val">{singleResult.floorplan.rooms.length} Rooms</div>
                      <div className="lbl">Room Density</div>
                    </div>
                    <div className="metric-card">
                      <div className="val">{singleResult.validation.score_percentage}%</div>
                      <div className="lbl">Validation Score</div>
                    </div>
                  </div>

                  {singleResult.validation.warnings && singleResult.validation.warnings.length > 0 && (
                    <div style={{ backgroundColor: '#0d1117', border: '1px solid #21262d', padding: '10px', borderRadius: '6px', fontSize: '0.82rem' }}>
                      <strong style={{ color: '#d29922' }}>Validation Audit & Warnings:</strong>
                      <ul style={{ margin: '6px 0 0 18px', padding: 0, color: '#8b949e' }}>
                        {singleResult.validation.warnings.map((w, idx) => (
                          <li key={idx}>{w}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="svg-display-card">
                <p style={{ color: '#8b949e' }}>Click "Generate 2D Floor Plan" to synthesize layout.</p>
              </div>
            )
          ) : (
            /* Model Comparison View */
            compareResult && compareResult.comparison ? (
              <div className="comparison-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
                {['gan', 'vae', 'diffusion', 'bsp_baseline'].map((mKey) => {
                  const mData = compareResult.comparison[mKey];
                  if (!mData) return null;
                  return (
                    <div key={mKey} className="comparison-card">
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#f0f6fc' }}>{mData.model_name}</h3>
                        <span className={`status-badge ${mData.is_trained_checkpoint ? 'badge-success' : 'badge-warning'}`}>
                          {mData.is_trained_checkpoint ? 'Checkpoint' : 'Fallback'}
                        </span>
                      </div>

                      <div style={{ height: '320px', border: '1px solid #21262d', borderRadius: '6px', overflow: 'hidden', display: 'flex', justifyContent: 'center', backgroundColor: '#0d1117' }}>
                        <div dangerouslySetInnerHTML={{ __html: mData.svg_content }} style={{ width: '100%', height: '100%' }} />
                      </div>

                      <div style={{ fontSize: '0.8rem', display: 'flex', flexDirection: 'column', gap: '4px', color: '#8b949e' }}>
                        <div><strong>Validation Score:</strong> <span style={{ color: '#3fb950' }}>{mData.validation.score_percentage}%</span></div>
                        <div><strong>Rooms Generated:</strong> {mData.floorplan.rooms.length}</div>
                        <div><strong>Unused Area Ratio:</strong> {(mData.validation.unused_area_ratio * 100).toFixed(1)}%</div>
                        <div><strong>Overlaps Count:</strong> {mData.validation.overlaps_count}</div>
                        <div><strong>Latency:</strong> {mData.generation_time_ms} ms</div>
                      </div>

                      <button className="btn-secondary" style={{ marginTop: 'auto' }} onClick={() => downloadSVG(mData.svg_content, `floorplan_${mKey}.svg`)}>
                        Download SVG
                      </button>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="svg-display-card">
                <p style={{ color: '#8b949e' }}>Click "Generate 2D Floor Plan" to run comparative evaluation across GAN, VAE, Diffusion, and BSP Baseline.</p>
              </div>
            )
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
