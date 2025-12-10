from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import paramiko
import asyncio
import json

app = FastAPI()

# React(3000번 포트)에서 오는 요청 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_remote_cpu_usage(ssh):
    """원격 서버에서 CPU 사용량을 가져오는 SSH 명령어 실행"""
    # /proc/stat 파일을 읽어서 계산하는 방식이 가장 가볍습니다.
    # 여기서는 데모를 위해 'top' 명령어를 간단히 파싱하거나 임의의 명령어를 씁니다.
    # 실제로는 'grep "cpu " /proc/stat' 결과를 파싱하는 것이 정석입니다.
    stdin, stdout, stderr = ssh.exec_command("grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}'")
    usage = stdout.read().decode().strip()
    return usage if usage else "0"

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 1. 초기 접속 정보 수신 (IP, User, Password)
        data = await websocket.receive_text()
        credentials = json.loads(data)
        
        ip = credentials.get("ip")
        username = credentials.get("username")
        password = credentials.get("password")

        # 2. SSH 연결 시도
        try:
            ssh_client.connect(ip, username=username, password=password, timeout=5)
            await websocket.send_text(json.dumps({"status": "connected", "message": f"Connected to {ip}"}))
        except Exception as e:
            await websocket.send_text(json.dumps({"status": "error", "message": str(e)}))
            return

        # 3. 주기적으로 데이터 전송 (무한 루프)
        while True:
            cpu_usage = get_remote_cpu_usage(ssh_client)
            
            # 클라이언트로 데이터 전송
            payload = {
                "status": "monitoring",
                "ip": ip,
                "cpu": cpu_usage,
                "timestamp": asyncio.get_event_loop().time()
            }
            await websocket.send_text(json.dumps(payload))
            
            # 2초 대기 (비동기)
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh_client.close()