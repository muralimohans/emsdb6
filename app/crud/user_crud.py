# app/crud/user_crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User

class UserCRUD:
    async def get_by_email(self, db: AsyncSession, email: str):
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, email: str, hashed_password: str):
        new_user = User(email=email, hashed_password=hashed_password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user


# 👇 instantiate a single CRUD object to use in routes
user_crud = UserCRUD()
