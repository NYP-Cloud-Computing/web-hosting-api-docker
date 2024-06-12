from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Dict


app = FastAPI(
    title="Project Planner API",
    description="A planner to organize your projects",
    version="1.0"
)


TODOS: Dict[str, Dict[str, str]] = {
    "1": {"task": "Build an API", "due_date": "2024-05-01"},
    "2": {"task": "Check with the team meeting", "due_date": "2024-06-02"},
    "3": {"task": "Deploy this API and inform clients", "due_date": "2024-07-03"},
}


TASKCOMPLETED = 0


def abort_if_todo_doesnt_exist(todo_id: str):
    if todo_id not in TODOS:
        raise HTTPException(status_code=404, detail=f"Todo {todo_id} doesn't exist")


class TodoModel(BaseModel):
    task: str = Field(..., example="Build an API")
    due_date: date = Field(..., example="2024-05-01")


@app.get("/tasks/{todo_id}", response_model=TodoModel)
async def get_task(todo_id: str):
    """Retrieve specific task"""
    abort_if_todo_doesnt_exist(todo_id)
    return TODOS[todo_id]


@app.delete("/tasks/{todo_id}", status_code=204)
async def delete_task(todo_id: str):
    """Delete a task"""
    abort_if_todo_doesnt_exist(todo_id)
    del TODOS[todo_id]
    return None


@app.put("/tasks/{todo_id}", response_model=TodoModel)
async def update_task(todo_id: str, task: str = Form(...), due_date: str = Form(...)):
    """Update a task"""
    abort_if_todo_doesnt_exist(todo_id)
    try:
        datetime.strptime(due_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format is not correct, please use YYYY-MM-DD")
    TODOS[todo_id] = {"task": task, "due_date": due_date}
    return TODOS[todo_id]


@app.post("/tasks/{todo_id}/complete", status_code=200)
async def complete_task(todo_id: str):
    """Complete a task"""
    global TASKCOMPLETED
    abort_if_todo_doesnt_exist(todo_id)
    TASKCOMPLETED += 1
    del TODOS[todo_id]
    return {"message": f"Task completed for Todo ID: {todo_id}"}


@app.get("/tasks/", response_model=Dict[str, TodoModel])
async def list_tasks():
    """List all tasks"""
    return TODOS


@app.post("/tasks/", response_model=TodoModel, status_code=201)
async def create_task(task: str = Form(...), due_date: str = Form(...)):
    """Create a task"""
    try:
        datetime.strptime(due_date, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(status_code=400, detail="Date format is not correct, please use YYYY-MM-DD")
    todo_id = str(len(TODOS) + 1)
    TODOS[todo_id] = {"task": task, "due_date": due_date}
    return TODOS[todo_id]


@app.get("/tasks/completed", response_model=str)
async def get_completed_tasks():
    """Display the number of tasks completed"""
    return f"You completed {TASKCOMPLETED} tasks"
