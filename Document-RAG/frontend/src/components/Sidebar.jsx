import { useState } from 'react';
import { Database, UploadCloud, Link as LinkIcon, Settings } from 'lucide-react';

function Sidebar({ onInitUrls, onInitFiles, status, isLoading }) {
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [selectedFiles, setSelectedFiles] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFiles(e.target.files);
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h1><Database size={20} /> Document RAG</h1>
      </div>
      
      <div className="sidebar-content">
        <div className="config-section">
          <h2><LinkIcon size={16} style={{display: 'inline', marginRight: 8, verticalAlign: 'text-bottom'}}/> Default Documents</h2>
          <p style={{fontSize: '0.8rem', color: 'var(--base0)', marginBottom: 12}}>Load predefined URLs configured in your environment.</p>
          <button 
            className="btn btn-primary" 
            onClick={onInitUrls}
            disabled={isLoading}
          >
            {isLoading ? <div className="loader"></div> : 'Load Default URLs'}
          </button>
        </div>

        <div className="config-section">
          <h2><UploadCloud size={16} style={{display: 'inline', marginRight: 8, verticalAlign: 'text-bottom'}}/> Custom Files</h2>
          <p style={{fontSize: '0.8rem', color: 'var(--base0)', marginBottom: 12}}>Upload custom PDFs or Text files to analyze.</p>
          
          <div className="form-group">
            <label>Files</label>
            <input 
              type="file" 
              multiple 
              accept=".pdf,.txt,.md"
              onChange={handleFileChange}
              style={{fontSize: '0.8rem', width: '100%'}}
            />
          </div>

          <details style={{marginBottom: 16}}>
            <summary style={{fontSize: '0.8rem', cursor: 'pointer', color: 'var(--blue)'}}>
              <Settings size={14} style={{display: 'inline', marginRight: 4, verticalAlign: 'middle'}}/>
              Advanced Options
            </summary>
            <div style={{marginTop: 12}}>
              <div className="form-group">
                <label>Chunk Size: {chunkSize}</label>
                <input type="range" min="100" max="2000" step="100" value={chunkSize} onChange={(e) => setChunkSize(e.target.value)} />
              </div>
              <div className="form-group">
                <label>Chunk Overlap: {chunkOverlap}</label>
                <input type="range" min="0" max="500" step="10" value={chunkOverlap} onChange={(e) => setChunkOverlap(e.target.value)} />
              </div>
            </div>
          </details>

          <button 
            className="btn btn-primary" 
            onClick={() => onInitFiles(selectedFiles, chunkSize, chunkOverlap)}
            disabled={isLoading || !selectedFiles || selectedFiles.length === 0}
          >
            {isLoading ? <div className="loader"></div> : 'Process Files'}
          </button>
        </div>

        <div className={`status-indicator ${status.type === 'error' ? 'error' : ''}`}>
          <strong>Status:</strong><br/>
          {status.message}
        </div>
      </div>
    </div>
  );
}

export default Sidebar;
