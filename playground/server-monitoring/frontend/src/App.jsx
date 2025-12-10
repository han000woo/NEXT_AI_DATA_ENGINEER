import { useState, useEffect, useRef } from 'react'

function App() {
  const [formData, setFormData] = useState({ ip: '', username: '', password: '' });
  const [logs, setLogs] = useState([]);
  const [status, setStatus] = useState('idle'); // idle, connecting, monitoring, error
  const ws = useRef(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const startMonitoring = () => {
    if (ws.current) ws.current.close();

    // FastAPI 웹소켓 주소
    ws.current = new WebSocket('ws://localhost:8000/ws/monitor');

    ws.current.onopen = () => {
      setStatus('connecting');
      // 연결되자마자 접속 정보 전송
      ws.current.send(JSON.stringify(formData));
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.status === 'connected') {
        setStatus('monitoring');
      } else if (data.status === 'error') {
        setStatus('error');
        alert(`Connection Failed: ${data.message}`);
        ws.current.close();
      } else if (data.status === 'monitoring') {
        // 모니터링 데이터 수신 (최신 로그가 위로 오게)
        setLogs((prev) => [`[${data.ip}] CPU Usage: ${parseFloat(data.cpu).toFixed(2)}%`, ...prev.slice(0, 9)]);
      }
    };

    ws.current.onclose = () => setStatus('idle');
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
      <h1>Server Monitor 🖥️</h1>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
        <input name="ip" placeholder="Server IP (e.g., 192.168.0.5)" value={formData.ip} onChange={handleChange} style={{padding: '8px'}} />
        <input name="username" placeholder="SSH Username (e.g., root)" value={formData.username} onChange={handleChange} style={{padding: '8px'}} />
        <input type="password" name="password" placeholder="SSH Password" value={formData.password} onChange={handleChange} style={{padding: '8px'}} />
        
        <button onClick={startMonitoring} disabled={status === 'monitoring'} style={{padding: '10px', cursor: 'pointer'}}>
          {status === 'monitoring' ? 'Monitoring...' : 'Start Monitoring'}
        </button>
      </div>

      <div style={{ border: '1px solid #ccc', padding: '1rem', borderRadius: '8px', minHeight: '200px', background: '#f9f9f9' }}>
        <h3>Live Status: {status.toUpperCase()}</h3>
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {logs.map((log, index) => (
            <li key={index} style={{ padding: '5px 0', borderBottom: '1px solid #eee' }}>{log}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default App