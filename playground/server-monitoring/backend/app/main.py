from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import paramiko
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_linux_stats(ssh):
    """원격 서버의 CPU, 메모리, 상위 프로세스, 서비스 상태 조회"""
    stats = {}

    try:
        # 1. CPU 사용량 (grep 방식이 가장 빠름)
        _, stdout, _ = ssh.exec_command("grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage}'")
        stats['cpu'] = stdout.read().decode().strip()

        # 2. 메모리 사용량 (free 명령어)
        # 결과: total used free ...
        _, stdout, _ = ssh.exec_command("free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'")
        stats['memory'] = stdout.read().decode().strip()

        # 3. CPU 많이 쓰는 Top 5 프로세스
        # ps 명령 옵션: pid, command, %cpu, %mem (cpu 내림차순 정렬)
        cmd_ps = "ps -Ao pid,comm,pcpu,pmem --sort=-pcpu | head -n 6"
        _, stdout, _ = ssh.exec_command(cmd_ps)
        process_output = stdout.read().decode().strip().split('\n')
        
        processes = []
        if len(process_output) > 1:
            for line in process_output[1:]: # 헤더 제외
                parts = line.split()
                if len(parts) >= 4:
                    processes.append({
                        "pid": parts[0],
                        "name": parts[1],
                        "cpu": parts[2],
                        "mem": parts[3]
                    })
        stats['processes'] = processes

        # 4. 주요 서비스 상태 확인 (예: docker, sshd, nginx)
        # 원하는 서비스 목록을 배열에 넣으세요.
        target_services = ["docker", "sshd", "nginx", "cron"]
        service_cmd = f"systemctl is-active {' '.join(target_services)}"
        _, stdout, _ = ssh.exec_command(service_cmd)
        service_statuses = stdout.read().decode().strip().split('\n')
        
        services = []
        for i, name in enumerate(target_services):
            # 결과가 active면 실행중, 아니면 중지/없는 서비스
            status = service_statuses[i] if i < len(service_statuses) else "unknown"
            services.append({"name": name, "status": status})
        
        stats['services'] = services

    except Exception as e:
        print(f"Command Error: {e}")
        return None

    return stats

@app.websocket("/ws/monitor")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        data = await websocket.receive_text()
        creds = json.loads(data)
        
        ssh_client.connect(creds.get("ip"), username=creds.get("username"), password=creds.get("password"), timeout=5)
        await websocket.send_text(json.dumps({"status": "connected"}))

        while True:
            server_stats = get_linux_stats(ssh_client)
            
            if server_stats:
                payload = {
                    "status": "monitoring",
                    "ip": creds.get("ip"),
                    "data": server_stats
                }
                await websocket.send_text(json.dumps(payload))
            
            await asyncio.sleep(2) # 2초 주기 갱신

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(json.dumps({"status": "error", "message": str(e)}))
    finally:
        ssh_client.close()