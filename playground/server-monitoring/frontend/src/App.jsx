import { useState, useRef } from 'react'

function App() {
  const [formData, setFormData] = useState({ ip: '', username: '', password: '' });
  const [serverData, setServerData] = useState(null);
  const [status, setStatus] = useState('idle');
  const ws = useRef(null);

  const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

  const startMonitoring = () => {
    if (ws.current) ws.current.close();
    ws.current = new WebSocket('ws://localhost:8000/ws/monitor');

    ws.current.onopen = () => {
      setStatus('connecting');
      ws.current.send(JSON.stringify(formData));
    };

    ws.current.onmessage = (event) => {
      const response = JSON.parse(event.data);
      if (response.status === 'connected') setStatus('monitoring');
      else if (response.status === 'error') {
        alert(response.message);
        setStatus('idle');
      } 
      else if (response.status === 'monitoring') {
        setServerData(response.data);
      }
    };

    ws.current.onclose = () => setStatus('idle');
  };

  // 서비스 상태에 따라 색상 반환
  const getStatusColor = (status) => status === 'active' ? '#4caf50' : '#f44336';

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto', padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1 style={{ textAlign: 'center' }}>🚀 Linux Server Monitor</h1>

      {/* 접속 폼 */}
      <div style={{ display: 'flex', gap: '10px', justifyContent: 'center', marginBottom: '30px' }}>
        <input name="ip" placeholder="IP Address" value={formData.ip} onChange={handleChange} style={inputStyle} />
        <input name="username" placeholder="Username" value={formData.username} onChange={handleChange} style={inputStyle} />
        <input type="password" name="password" placeholder="Password" value={formData.password} onChange={handleChange} style={inputStyle} />
        <button onClick={startMonitoring} disabled={status === 'monitoring'} style={buttonStyle}>
          {status === 'monitoring' ? 'Monitoring...' : 'Connect'}
        </button>
      </div>

      {status === 'monitoring' && serverData && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          
          {/* 1. 시스템 리소스 카드 */}
          <div style={cardStyle}>
            <h3>📊 System Resources</h3>
            <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
              <div style={{ textAlign: 'center' }}>
                <div style={gaugeStyle}>{parseFloat(serverData.cpu).toFixed(1)}%</div>
                <div>CPU Usage</div>
              </div>
              <div style={{ textAlign: 'center' }}>
                <div style={gaugeStyle}>{parseFloat(serverData.memory).toFixed(1)}%</div>
                <div>Memory Usage</div>
              </div>
            </div>
          </div>

          {/* 2. 주요 서비스 상태 */}
          <div style={cardStyle}>
            <h3>⚙️ Service Status</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {serverData.services.map((svc) => (
                <li key={svc.name} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #eee' }}>
                  <strong>{svc.name}</strong>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '12px', 
                    color: 'white', 
                    fontSize: '0.8rem',
                    backgroundColor: getStatusColor(svc.status) 
                  }}>
                    {svc.status.toUpperCase()}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          {/* 3. 프로세스 목록 (하단 전체) */}
          <div style={{ ...cardStyle, gridColumn: 'span 2' }}>
            <h3>🔥 Top 5 CPU Processes</h3>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ background: '#f5f5f5' }}>
                  <th style={thStyle}>PID</th>
                  <th style={thStyle}>Name</th>
                  <th style={thStyle}>CPU %</th>
                  <th style={thStyle}>MEM %</th>
                </tr>
              </thead>
              <tbody>
                {serverData.processes.map((proc) => (
                  <tr key={proc.pid}>
                    <td style={tdStyle}>{proc.pid}</td>
                    <td style={tdStyle}>{proc.name}</td>
                    <td style={tdStyle}>{proc.cpu}%</td>
                    <td style={tdStyle}>{proc.mem}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </div>
      )}
    </div>
  )
}

// 간단한 스타일 객체들
const inputStyle = { padding: '10px', borderRadius: '5px', border: '1px solid #ddd' };
const buttonStyle = { padding: '10px 20px', borderRadius: '5px', border: 'none', background: '#007bff', color: 'white', cursor: 'pointer' };
const cardStyle = { padding: '20px', borderRadius: '10px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)', background: 'white' };
const gaugeStyle = { fontSize: '2rem', fontWeight: 'bold', color: '#007bff', marginBottom: '10px' };
const thStyle = { padding: '10px', borderBottom: '2px solid #eee' };
const tdStyle = { padding: '10px', borderBottom: '1px solid #eee' };

export default App