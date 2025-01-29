from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()
proxy_stats = {"requests_served": 0, "success_count": 0, "failure_count": 0}

class StatsUpdate(BaseModel):
    status: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/stats")
async def stats():
    return proxy_stats

@app.middleware("http")
async def track_requests(request: Request, call_next):
    proxy_stats["requests_served"] += 1
    response = await call_next(request)
    return response

@app.post("/update_stats")
async def update_stats(data: StatsUpdate):
    if data.status == "success":
        proxy_stats["success_count"] += 1
    elif data.status == "failure":
        proxy_stats["failure_count"] += 1
    return {"message": "Stats updated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)