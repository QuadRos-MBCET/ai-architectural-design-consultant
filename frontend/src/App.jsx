import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [prompt, setPrompt] = useState(
    'Design a modern sustainable college library in a tropical hot-humid climate with a reading hall, computer section, discussion rooms, librarian office, storage, toilets, natural ventilation, and solar shading.'
  );
  const [isLoading, setIsLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const [consultantData, setConsultantData] = useState(null);
  const [activeFloor, setActiveFloor] = useState('ground'); // 'ground' or 'top'
  const [workflowTab, setWorkflowTab] = useState('rag'); // 'rag' or 'gan'

  useEffect(() => {
    handleRunPipeline();
  }, []);

  const handleRunPipeline = async () => {
    setIsLoading(true);
    setErrorMsg('');
    setStatusMsg('Running FAISS vector retrieval & architectural RAG pipeline...');

    try {
      const res = await fetch(`${API_BASE}/api/consultant/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });

      if (!res.ok) throw new Error(`API returned status ${res.status}`);
      const data = await res.json();
      setConsultantData(data);
      setStatusMsg('Successfully generated context-aware architectural design consultation & blueprint.');
    } catch (err) {
      setErrorMsg(`Connection Error: Unable to reach backend server at ${API_BASE}. Please ensure the local FastAPI backend is running (run_project.bat) or VITE_API_URL is configured.`);
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
            <div className="prompt-guide-box">
              <div className="prompt-guide-title">
                <span className="info-icon">💡</span> <strong>Supported Prompt Structure:</strong>
              </div>
              <div className="prompt-guide-list">
                <div className="guide-item">
                  <span className="guide-label">🏢 Typologies:</span>
                  <span className="guide-val">Hospital, Hotel, Restaurant, Police Station, Library, House, School, Office</span>
                </div>
                <div className="guide-item">
                  <span className="guide-label">🚪 Rooms & Counts:</span>
                  <span className="guide-val">e.g. <em>3 holding cells, ICU ward, reading hall, commercial kitchen, 2 suites</em></span>
                </div>
                <div className="guide-item">
                  <span className="guide-label">📏 Dimensions & Floors:</span>
                  <span className="guide-val">e.g. <em>30m x 20m, 2 floors</em></span>
                </div>
                <div className="guide-item">
                  <span className="guide-label">🌿 Climate & Site:</span>
                  <span className="guide-val">e.g. <em>tropical climate, hot-humid, arid, urban site</em></span>
                </div>
              </div>
            </div>
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
          {consultantData ? (
              <div className="consultant-results-view">
                {/* Overall Project Workflow Dropdown Accordion */}
                <details className="workflow-dropdown-card" open>
                  <summary>
                    <span>🔄 <strong>Overall Project Architectural Workflow</strong></span>
                    <span style={{ fontSize: '0.8rem', color: '#58a6ff' }}>Click to Toggle View</span>
                  </summary>

                  <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                    <button
                      className={`btn-secondary ${workflowTab === 'rag' ? 'active-tab' : ''}`}
                      onClick={() => setWorkflowTab('rag')}
                      style={{
                        backgroundColor: workflowTab === 'rag' ? '#1f6beb' : '#21262d',
                        color: '#ffffff',
                        fontSize: '0.82rem',
                        padding: '6px 12px',
                        fontWeight: '600'
                      }}
                    >
                      🌐 5-Stage RAG Pipeline Workflow
                    </button>
                    <button
                      className={`btn-secondary ${workflowTab === 'gan' ? 'active-tab' : ''}`}
                      onClick={() => setWorkflowTab('gan')}
                      style={{
                        backgroundColor: workflowTab === 'gan' ? '#1f6beb' : '#21262d',
                        color: '#ffffff',
                        fontSize: '0.82rem',
                        padding: '6px 12px',
                        fontWeight: '600'
                      }}
                    >
                      🧠 PyTorch cGAN & Diffusion Neural Workflow
                    </button>
                  </div>

                  {workflowTab === 'rag' ? (
                    <div className="workflow-steps-grid">
                      <div className="workflow-step-item">
                        <span className="step-num">STAGE 01</span>
                        <div className="step-title">NLP Requirement Parsing</div>
                        <p className="step-desc">Parses building typology, room program, dimensions, and prompt hash seed.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num">STAGE 02</span>
                        <div className="step-title">FAISS Vector Retrieval</div>
                        <p className="step-desc">Queries FAISS vector index & typology database for precedent case studies.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num">STAGE 03</span>
                        <div className="step-title">RAG Context Refinement</div>
                        <p className="step-desc">Extracts passive climate rules and enforces 6m structural column grid bounds.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num">STAGE 04</span>
                        <div className="step-title">Generative Model Synthesis</div>
                        <p className="step-desc">PyTorch DDPM Diffusion / cGAN model synthesizes 2D spatial bounding boxes.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num">STAGE 05</span>
                        <div className="step-title">CAD Blueprint Rendering</div>
                        <p className="step-desc">Solves geometric overlaps and renders multi-tier, multi-floor 2D CAD SVG blueprints.</p>
                      </div>
                    </div>
                  ) : (
                    <div className="workflow-steps-grid">
                      <div className="workflow-step-item">
                        <span className="step-num" style={{ color: '#a371f7' }}>cGAN STEP 01</span>
                        <div className="step-title">Condition Vector (c ∈ ℝ²⁴)</div>
                        <p className="step-desc">Encodes building dimensions & 22 room typology counts into PyTorch condition tensor.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num" style={{ color: '#a371f7' }}>cGAN STEP 02</span>
                        <div className="step-title">Latent Sampling (z ∈ ℝ⁶⁴)</div>
                        <p className="step-desc">Samples 64-dim Gaussian random noise vector z ~ N(0, I) to seed spatial variety.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num" style={{ color: '#a371f7' }}>cGAN STEP 03</span>
                        <div className="step-title">Generator Forward Pass (G)</div>
                        <p className="step-desc">Passes concatenated [z, c] through FC layers, BatchNorm1d, and ReLU to output (16 × 26) tensor.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num" style={{ color: '#a371f7' }}>cGAN STEP 04</span>
                        <div className="step-title">Sigmoid & Softmax Decoding</div>
                        <p className="step-desc">Applies Sigmoid to [x, y, w, h] coords and Softmax across 22 room category channels.</p>
                      </div>
                      <div className="workflow-step-item">
                        <span className="step-num" style={{ color: '#a371f7' }}>cGAN STEP 05</span>
                        <div className="step-title">Discriminator (D) Validation</div>
                        <p className="step-desc">Adversarial Discriminator evaluates spatial realism against real floor plan dataset.</p>
                      </div>
                    </div>
                  )}
                </details>

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
                      <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#f0f6fc' }}>
                        Context-Aware 2D Architectural Blueprint
                        {consultantData.floors_count > 1 && ` (${consultantData.floors_count}-Story Building)`}
                      </h3>
                      <span className="status-badge badge-success">Suitability Score: {consultantData.suitability_score}%</span>
                    </div>
                    <button
                      className="btn-secondary"
                      onClick={() => {
                        const targetPlan = activeFloor === 'top' && consultantData.top_floorplan ? consultantData.top_floorplan : consultantData.floorplan;
                        downloadSVG(targetPlan.svg_content || '', `${activeFloor}_floorplan.svg`);
                      }}
                    >
                      Download SVG
                    </button>
                  </div>

                  {consultantData.top_floorplan && (
                    <div className="floor-tab-bar" style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                      <button
                        className={`btn-secondary ${activeFloor === 'ground' ? 'active-tab' : ''}`}
                        onClick={() => setActiveFloor('ground')}
                        style={{
                          backgroundColor: activeFloor === 'ground' ? '#238636' : '#21262d',
                          color: '#ffffff',
                          fontWeight: '600'
                        }}
                      >
                        🏢 Ground Floor (Level 1)
                      </button>
                      <button
                        className={`btn-secondary ${activeFloor === 'top' ? 'active-tab' : ''}`}
                        onClick={() => setActiveFloor('top')}
                        style={{
                          backgroundColor: activeFloor === 'top' ? '#238636' : '#21262d',
                          color: '#ffffff',
                          fontWeight: '600'
                        }}
                      >
                        🏙️ Top Floor (Level {consultantData.floors_count})
                      </button>
                    </div>
                  )}

                  <div className="svg-box" style={{ minHeight: '450px' }}>
                    <div
                      dangerouslySetInnerHTML={{
                        __html: (activeFloor === 'top' && consultantData.top_floorplan ? consultantData.top_floorplan : consultantData.floorplan).svg_content || ''
                      }}
                      style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center' }}
                    />
                  </div>
                </div>
              </div>
            ) : (
              <div className="placeholder-box">
                <p>Click "Run Architectural Analysis" to execute RAG retrieval and generate context-aware design guidance.</p>
              </div>
            )}
        </section>
      </main>
    </div>
  );
}

export default App;
