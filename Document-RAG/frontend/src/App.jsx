import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

// Point to the backend API
const API_URL = import.meta.env.DEV ? 'http://localhost:8000' : '';

function App() {
  const [history, setHistory] = useState([]);
  const [isReady, setIsReady] = useState(false);
  const [systemStatus, setSystemStatus] = useState({ type: 'info', message: 'System not initialized. Please load documents.' });
  const [isLoading, setIsLoading] = useState(false);

  const handleInitUrls = async () => {
    setIsLoading(true);
    try {
      const res = await axios.post(`${API_URL}/api/init/urls`);
      setSystemStatus({ type: 'success', message: res.data.message });
      setIsReady(true);
    } catch (err) {
      setSystemStatus({ type: 'error', message: err.response?.data?.detail || err.message });
      setIsReady(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInitFiles = async (files, chunkSize, chunkOverlap) => {
    setIsLoading(true);
    try {
      const formData = new FormData();
      Array.from(files).forEach(f => formData.append('files', f));
      formData.append('chunk_size', chunkSize);
      formData.append('chunk_overlap', chunkOverlap);

      const res = await axios.post(`${API_URL}/api/init/files`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSystemStatus({ type: 'success', message: res.data.message });
      setIsReady(true);
    } catch (err) {
      setSystemStatus({ type: 'error', message: err.response?.data?.detail || err.message });
      setIsReady(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (question) => {
    if (!question.trim() || !isReady) return;

    // Optimistically add user message
    const newHistory = [...history, { role: 'user', content: question }];
    setHistory(newHistory);
    setIsLoading(true);

    try {
      const res = await axios.post(`${API_URL}/api/chat`, {
        question,
        history: history
      });
      
      // Update history with assistant's response and source docs
      setHistory([
        ...newHistory, 
        { 
          role: 'assistant', 
          content: res.data.answer,
          docs_text: res.data.docs_text,
          time: res.data.time
        }
      ]);
    } catch (err) {
      setHistory([
        ...newHistory,
        { role: 'assistant', content: `❌ Error: ${err.response?.data?.detail || err.message}` }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        onInitUrls={handleInitUrls}
        onInitFiles={handleInitFiles}
        status={systemStatus}
        isLoading={isLoading}
      />
      <ChatWindow 
        history={history}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        isReady={isReady}
      />
    </div>
  );
}

export default App;
