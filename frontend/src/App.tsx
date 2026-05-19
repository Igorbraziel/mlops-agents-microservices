import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import './App.css'

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const DEMO_QUESTIONS = [
  {
    title: "Simple Search",
    question: "O que são microserviços e qual a diferença em relação a um pipeline?"
  },
  {
    title: "Full Report",
    question: "Pesquise sobre segurança de segredos e cold starts, depois gere um relatório chamado 'Boas Práticas em Produção' com o que encontrar. Autor: Grupo MLOps"
  },
  {
    title: "Cloud Run & Agno",
    question: "Como os agentes do Agno podem usar ferramentas hospedadas no Cloud Run?"
  }
];

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok) {
        throw new Error('Falha na comunicação com o orquestrador');
      }

      const data = await response.json();
      const assistantMessage: Message = { role: 'assistant', content: data.content };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = { 
        role: 'assistant', 
        content: `Error: ${error instanceof Error ? error.message : 'Unknown error'}` 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>MLOps Agents Dashboard</h1>
        <div className="header-badge">Multi-Agent Orchestrator</div>
      </header>

      <main className="app-main">
        <aside className="demo-sidebar">
          <h2>Demo Questions</h2>
          <p>Clique em uma pergunta para testar o time de agentes:</p>
          <div className="demo-list">
            {DEMO_QUESTIONS.map((item, index) => (
              <button 
                key={index} 
                className="demo-card"
                onClick={() => handleSend(item.question)}
                disabled={loading}
              >
                <strong>{item.title}</strong>
                <span>{item.question.substring(0, 60)}...</span>
              </button>
            ))}
          </div>
        </aside>

        <section className="chat-section">
          <div className="messages-container">
            {messages.length === 0 && (
              <div className="empty-state">
                <p>Selecione uma demo ao lado ou faça uma pergunta técnica sobre MLOps.</p>
              </div>
            )}
            {messages.map((msg, index) => (
              <div key={index} className={`message-bubble ${msg.role}`}>
                <div className="role-label">{msg.role === 'user' ? 'Você' : 'Orquestrador'}</div>
                <div className="message-content">
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            ))}
            {loading && (
              <div className="message-bubble assistant loading">
                <div className="role-label">Orquestrador</div>
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                </div>
              </div>
            )}
          </div>

          <form className="input-area" onSubmit={(e) => { e.preventDefault(); handleSend(input); }}>
            <input 
              type="text" 
              value={input} 
              onChange={(e) => setInput(e.target.value)}
              placeholder="Digite sua pergunta sobre MLOps..."
              disabled={loading}
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Enviar
            </button>
          </form>
        </section>
      </main>
    </div>
  )
}

export default App
