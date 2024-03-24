from typing import Optional, List, Union, Annotated
from sqlmodel import SQLModel, Field, create_engine, Session, select
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from poetry_todoapp import settings
from contextlib import asynccontextmanager


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None

engine = create_engine(str(settings.DATABASE_URL), echo=True)

# Create DB and tables if not exist
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://0.0.0.0:8000", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

# Allow all origins for simplicity (in production, specify your frontend origin)
origins = [
    "http://localhost:3000",  # The default location for the Next.js app
    "http://localhost:8000",  # Allow requests from the same origin as well
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# Dependency
def get_session():
    with Session(engine) as session:
        yield session


@app.post("/tasks/", response_model=Task)
async def create_task(task: Task, session: Annotated[Session, Depends(get_session)]):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/", response_model=List[Task])
async def read_tasks(session: Annotated[Session, Depends(get_session)]):
    tasks = session.exec(select(Task)).all()
    return tasks

@app.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: Task, session: Annotated[Session, Depends(get_session)]):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = task_update.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, session: Annotated[Session, Depends(get_session)]):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}





