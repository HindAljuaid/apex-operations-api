from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app import models
from app.database import Base, engine, get_db

REQUEST_COUNT = Counter(
    "apex_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "http_status"],
)

REQUEST_LATENCY = Histogram(
    "apex_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Apex Operations API",
    description="A demonstration API for DevOps engineering practices.",
    version="1.0.1",
)

@app.middleware("http")
async def record_metrics(request: Request, call_next):
    start_time = perf_counter()

    response = await call_next(request)

    if request.url.path != "/metrics":
        route = request.scope.get("route")
        endpoint = getattr(route, "path", "unmatched")

        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=str(response.status_code),
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint,
        ).observe(perf_counter() - start_time)

    return response

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    completed: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    completed: bool | None = None


@app.get("/")
def root():
    return {
        "application": "Apex Operations API",
        "status": "running",
        "version": "1.0.1",
    }


@app.get("/health/live")
def health_live():
    return {"status": "alive"}


@app.get("/health/ready")
def health_ready(db: Session = Depends(get_db)):
    try:
        db.execute(models.Task.__table__.select().limit(1))
        return {"status": "ready"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Database is not available",
        )


@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(models.Task).order_by(models.Task.id).all()


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = models.Task(**task.model_dump())
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


@app.get("/tasks/{task_id}")
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    updates = task_update.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )