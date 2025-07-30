"""
간단한 테스트용 FastAPI 서버
기본 연결 확인용
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test Server", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "Server is running"}

@app.get("/test")
async def test():
    return {"test": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002) 