from fastapi import Query


def get_pagination(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50)
) -> dict[str, int]:
    return {"skip": skip, "limit": limit}