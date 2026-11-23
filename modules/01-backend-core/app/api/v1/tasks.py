from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_pagination
from app.core.db import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
async def create_task(
    payload: TaskCreate, db: AsyncSession = Depends(get_db)
):
    new_task = Task(**payload.model_dump())
    db.add(new_task)
    await db.flush()  # Populates new_task.id and created_at without final commit
    await db.refresh(new_task)
    return new_task


@router.get(
    "",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks with pagination and status filter",
)
async def list_tasks(
    completed_only: Optional[bool] = Query(
        default=None, description="Filter by completion status"
    ),
    pagination: dict = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task)
    if completed_only is not None:
        query = query.where(Task.is_completed == completed_only)

    query = query.offset(pagination["skip"]).limit(pagination["limit"])
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.get(
    "/{task_id}", response_model=TaskResponse, summary="Get task by ID"
)
async def get_task(
    task_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found.",
        )
    return task


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update a task",
)
async def update_task(
    payload: TaskUpdate,
    task_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found.",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.flush()
    await db.refresh(task)
    return task


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: int = Path(..., ge=1), db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found.",
        )

    await db.delete(task)
    return None