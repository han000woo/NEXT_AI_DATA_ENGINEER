from fastapi import FastAPI, HTTPException
from app.schemas.models import GenerateRequest, LogSchema
from app.services.generator import LogGeneratorService
from typing import List

app = FastAPI(title="Log Generator API")


@app.post("/generate-logs", response_model=List[LogSchema])
def generate_logs(req: GenerateRequest):
    try:
        # 서비스 로직 호출
        data = LogGeneratorService.generate_random_logs(req.count)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
