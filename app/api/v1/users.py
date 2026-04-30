from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import TokenPayload, get_current_user
from app.core.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.get("/users/me", response_model=UserResponse)
async def get_me(
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    user, _ = await service.get_or_create(
        auth0_id=current_user.sub,
        email=current_user.email or "",
    )
    return UserResponse.model_validate(user)


@router.patch("/users/me", response_model=UserResponse)
async def update_me(
    body: UserUpdate,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    service = UserService(db)
    user = await service.update(
        auth0_id=current_user.sub,
        **body.model_dump(exclude_unset=True),
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.model_validate(user)
