from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.deps import get_pagination
from app.core.db import fake_db, get_next_id
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task"
)
async def create_task(payload: TaskCreate):
    task_id = get_next_id()
    task_dict = payload.model_dump()
    task_dict.update({
        "id": task_id,
        "is_completed": False,
        "created_at": datetime.now(timezone.utc)
    })
    fake_db[task_id] = task_dict
    return task_dict


@router.get(
    "",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks with pagination and status filter"
)
async def list_tasks(
    completed_only: Optional[bool] = Query(default=None, description="Filter by completion status"),
    pagination: dict = Depends(get_pagination)
):
    tasks = list(fake_db.values())
    if completed_only is not None:
        tasks = [t for t in tasks if t["is_completed"] == completed_only]

    start = pagination["skip"]
    end = start + pagination["limit"]
    return tasks[start:end]


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get task by ID"
)
async def get_task(task_id: int = Path(..., ge=1)):
    if task_id not in fake_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found."
        )
    return fake_db[task_id]


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update a task"
)
async def update_task(task_id: int, payload: TaskUpdate):
    if task_id not in fake_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found."
        )
    update_data = payload.model_dump(exclude_unset=True)
    fake_db[task_id].update(update_data)
    return fake_db[task_id]


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task"
)
async def delete_task(task_id: int):
    if task_id not in fake_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found."
        )
    del fake_db[task_id]
    return None