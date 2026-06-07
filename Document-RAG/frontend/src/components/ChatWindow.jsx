import { useState, useRef, useEffect } from 'react';
import { Send, ChevronDown, ChevronRight, Clock } from 'lucide-react';

function SourceAccordion({ docsText }) {
  const [isOpen, setIsOpen] = useState(false);
  if (!docsText) return null;

  return (
    <div className="source-docs-accordion">
      <div className="source-docs-header" onClick={() => setIsOpen(!isOpen)}>
        <span>Source Documents Used</span>
        {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
      </div>
      {isOpen && (
        <div className="source-docs-content">
          {docsText}
        </div>
      )}
    </div>
  );
}

function ChatWindow({ history, onSendMessage, isLoading, isReady }) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [history]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading && isReady) {
      onSendMessage(input);
      setInput("");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-history">
        {history.length === 0 ? (
          <div style={{textAlign: 'center', color: 'var(--base0)', marginTop: '20vh'}}>
            <h2>Welcome to RAG Search</h2>
            <p>Load some documents from the sidebar to get started.</p>
          </div>
        ) : (
          history.map((msg, idx) => (
            <div key={idx} className={`message-bubble ${msg.role === 'user' ? 'message-user' : 'message-assistant'}`}>
              <div style={{fontWeight: 600, marginBottom: 8, fontSize: '0.85rem', textTransform: 'uppercase', color: msg.role === 'user' ? 'var(--blue)' : 'var(--orange)'}}>
                {msg.role === 'user' ? 'You' : 'Assistant'}
                {msg.time && <span style={{float: 'right', color: 'var(--base1)'}}><Clock size={12} style={{display: 'inline', marginRight: 4}}/>{msg.time}</span>}
              </div>
              <div style={{whiteSpace: 'pre-wrap'}}>{msg.content}</div>
              
              {msg.docs_text && <SourceAccordion docsText={msg.docs_text} />}
            </div>
          ))
        )}
        {isLoading && history.length > 0 && history[history.length-1].role === 'user' && (
          <div className="message-bubble message-assistant">
            <div className="loader" style={{margin: '10px 0'}}></div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <form className="input-wrapper" onSubmit={handleSubmit}>
          <input 
            type="text" 
            className="chat-input" 
            placeholder={isReady ? "Ask a question about your documents..." : "Please initialize the system first..."}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!isReady || isLoading}
          />
          <button type="submit" className="send-btn" disabled={!isReady || isLoading || !input.trim()}>
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChatWindow;
