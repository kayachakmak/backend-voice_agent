from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_auth0_id(self, auth0_id: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.auth0_id == auth0_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        auth0_id: str,
        email: str,
        name: Optional[str] = None,
        picture: Optional[str] = None,
    ) -> tuple[User, bool]:
        user = await self.get_by_auth0_id(auth0_id)
        if user:
            return user, False

        user = User(
            auth0_id=auth0_id,
            email=email,
            name=name,
            picture=picture,
        )
        self.db.add(user)
        await self.db.flush()
        return user, True

    async def update(self, auth0_id: str, **kwargs: object) -> Optional[User]:
        user = await self.get_by_auth0_id(auth0_id)
        if not user:
            return None

        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await self.db.flush()
        return user
