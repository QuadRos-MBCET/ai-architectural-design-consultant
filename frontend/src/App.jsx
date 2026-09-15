import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ThreeViewer from './components/ThreeViewer';
import mermaid from 'mermaid';
import './App.css';

// Initialize mermaid with dark theme
mermaid.initialize({ startOnLoad: true, theme: 'dark', themeVariables: { primaryColor: '#0f1115', primaryTextColor: '#f8fafc', primaryBorderColor: '#3b82f6', lineColor: '#94a3b8' } });

function Mermaid({ chart }) {
  const ref = useRef(null);
  useEffect(() => {
    if (ref.current && chart) {
      const uniqueId = 'mermaid-' + Math.random().toString(36).substring(2, 9);
      mermaid.render(uniqueId, chart).then(({ svg }) => {
        if (ref.current) ref.current.innerHTML = svg;
      }).catch(err => {
        console.error("Mermaid syntax error:", err);
        if (ref.current) ref.current.innerHTML = `<div style="color:red">Mermaid Error: ${err.message}</div>`;
      });
    }
  }, [chart]);
  return <div ref={ref} className="mermaid" style={{ display: 'flex', justifyContent: 'center', padding: '2rem', backgroundColor: '#1a202c', borderRadius: '8px', border: '1px solid #2d3748', overflowX: 'auto', minHeight: '400px' }} />;
}

function App() {
  const [prompt, setPrompt] = useState('design a 2 floor eco friendly public library for a hot and humid climate with natural ventilation');
  const [reportData, setReportData] = useState(null);
  const [gen3dData, setGen3dData] = useState(null);
  const [selectedTab, setSelectedTab] = useState('systems'); // 'combined', 'systems', or index of floor
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');

  const generateDesign = async () => {
    setIsLoading(true);
    setError('');
    setReportData(null);
    setGen3dData(null);
    setSelectedTab('systems'); // default to systems diagram first!
    
    try {
      setStatus('Analyzing geometry & generating blueprints...');
      
      const extractRes = await fetch('http://localhost:8000/api/requirements/extract', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_prompt: prompt })
      });
      
      if (!extractRes.ok) throw new Error('Failed to extract geometry');
      const extractData = await extractRes.json();
      const jsonSpec = extractData.structured_json;
      
      setReportData(jsonSpec);
      
      setStatus('Extruding Multi-Story Massing Model...');
      const gen3dRes = await fetch('http://localhost:8000/api/design/generate-3d', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ structured_json: jsonSpec })
      });
      
      if (!gen3dRes.ok) throw new Error('Failed to generate models');
      const genData = await gen3dRes.json();
      
      setGen3dData(genData);
      setStatus('');
      
    } catch (err) {
      setError(err.message);
      setStatus('');
    } finally {
      setIsLoading(false);
    }
  };

  // Determine what to show based on selected tab
  let currentModelUrl = null;
  let currentBlueprintUrl = null;
  let viewTitle = "Procedural Visualizations";

  if (gen3dData) {
    if (selectedTab === 'combined') {
      currentModelUrl = `http://localhost:5173${gen3dData.combined_model_url}`;
      viewTitle = "Multi-Story Building View";
    } else if (selectedTab === 'systems') {
      viewTitle = "Climate & Systems Architecture";
    } else {
      const floor = gen3dData.floors[selectedTab];
      currentModelUrl = `http://localhost:5173${floor.model_url}`;
      currentBlueprintUrl = `http://localhost:5173${floor.blueprint_url}`;
      viewTitle = `${floor.name} View`;
    }
  }

  const TabButton = ({ label, active, onClick }) => (
    <button 
      onClick={onClick}
      style={{ 
        padding: '8px 16px', 
        borderRadius: '4px', 
        border: '1px solid #334155', 
        cursor: 'pointer', 
        backgroundColor: active ? '#10b981' : '#1e293b', 
        color: active ? '#fff' : '#94a3b8', 
        fontWeight: 'bold',
        transition: 'all 0.2s'
      }}
    >
      {label}
    </button>
  );

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>AI Architectural Consultant</h1>
        <p>Generative Retrieval-Augmented 3D Design Pipeline</p>
      </header>

      <main className="main-content">
        {/* Left Column: Requirements */}
        <section className="column req-column">
          <h2>Project Requirements</h2>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe the architectural project..."
            rows={8}
            className="prompt-input"
          />
          <button 
            onClick={generateDesign} 
            disabled={isLoading}
            className="generate-btn"
          >
            {isLoading ? 'Processing...' : 'Generate Multi-Story Design'}
          </button>
          
          {status && <div className="status-msg">{status}</div>}
          {error && <div className="error-msg">{error}</div>}

          {/* Materials Estimate Section */}
          {reportData && reportData.materials_estimate && (
            <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#1e293b', borderRadius: '8px', border: '1px solid #334155' }}>
              <h3 style={{ marginTop: 0, color: '#f1f5f9', fontSize: '1.1rem' }}>Bill of Materials (INR)</h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px', fontSize: '0.85rem' }}>
                <thead>
                  <tr style={{ backgroundColor: '#0f1115', textAlign: 'left' }}>
                    <th style={{ padding: '8px', color: '#94a3b8' }}>Item</th>
                    <th style={{ padding: '8px', color: '#94a3b8' }}>Qty</th>
                    <th style={{ padding: '8px', color: '#94a3b8' }}>Rate</th>
                    <th style={{ padding: '8px', color: '#94a3b8' }}>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.materials_estimate.map((mat, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid #334155' }}>
                      <td style={{ padding: '8px', color: '#cbd5e1' }}>{mat.item}</td>
                      <td style={{ padding: '8px', color: '#94a3b8' }}>{mat.quantity} {mat.unit}</td>
                      <td style={{ padding: '8px', color: '#94a3b8' }}>₹{mat.present_rate.toLocaleString('en-IN')}</td>
                      <td style={{ padding: '8px', fontWeight: 'bold', color: '#10b981' }}>₹{mat.total_cost.toLocaleString('en-IN', {maximumFractionDigits: 0})}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Center Column: 3D Viewer & 2D Blueprint */}
        <section className="column viewer-column" style={{ position: 'relative' }}>
          <h2>{viewTitle}</h2>
          
          {/* Floor Selector Tabs */}
          {gen3dData && (
            <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', padding: '10px', backgroundColor: '#0f1115', borderRadius: '6px', border: '1px solid #334155' }}>
              <TabButton label="Systems Diagram" active={selectedTab === 'systems'} onClick={() => setSelectedTab('systems')} />
              <TabButton label="Entire Building" active={selectedTab === 'combined'} onClick={() => setSelectedTab('combined')} />
              {gen3dData.floors.map((floor, idx) => (
                <TabButton key={idx} label={floor.name} active={selectedTab === idx} onClick={() => setSelectedTab(idx)} />
              ))}
            </div>
          )}

          {selectedTab === 'systems' && reportData && reportData.systems_diagram && (
            <Mermaid chart={reportData.systems_diagram} />
          )}

          {currentBlueprintUrl && selectedTab !== 'systems' && (
            <div style={{ padding: '1rem', borderBottom: '1px solid #334155', backgroundColor: '#1a202c', textAlign: 'center', marginBottom: '15px', borderRadius: '8px' }}>
              <h3 style={{ marginTop: 0, fontSize: '1.1rem', color: '#f1f5f9' }}>2D Structural Blueprint</h3>
              <img src={currentBlueprintUrl} alt="2D Floor Plan SVG" style={{ maxWidth: '100%', border: '1px solid #475569', borderRadius: '4px', backgroundColor: '#f8fafc' }} />
            </div>
          )}

          {selectedTab !== 'systems' && (
            <div className="viewer-wrapper">
              <h3 style={{ position: 'absolute', top: '10px', left: '15px', zIndex: 10, margin: 0, fontSize: '1.0rem', color: '#f1f5f9', background: 'rgba(15, 17, 21, 0.8)', padding: '6px 12px', borderRadius: '6px', border: '1px solid #334155' }}>CAD Rendering</h3>
              <ThreeViewer modelUrl={currentModelUrl} />
            </div>
          )}
        </section>

        
      </main>
    </div>
  );
}

export default App;
