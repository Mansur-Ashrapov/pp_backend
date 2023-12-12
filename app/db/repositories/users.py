from typing import Optional

from app.db.exceptions import EntityDoesNotExist, EntityAlreadyExist
from app.db.tables import User as UserModel
from app.db.repositories.base import BaseRepository
from app.models.schemas.users import UserRegister, UserInDB
from app.db.utils import create_id_len_five


class UserRepository(BaseRepository):
    # async def get_users(self) -> list[UserInDB]:
    #     users = await self.database.fetch_all(UserModel.select())
    #     return [ UserInDB(
    #         id=user.id,
    #         username=user.username,
    #         fullname=user.fullname,
    #         email=user.email,
    #     ) for user in users ]

    async def get_user_by_id(self, id: str) -> UserInDB:
        user = await self.database.fetch_one(UserModel.select().where(UserModel.c.id == id))
        if user:
            return UserInDB(
                id=user.id,
                username=user.username,
                fullname=user.fullname,
                password_hash=user.password_hash,
                email=user.email,
            )
        raise EntityDoesNotExist(f"user with id {id} does not exist")

    async def get_user_by_username(self, username: str) -> UserInDB:
        user = await self.database.fetch_one(UserModel.select().where(UserModel.c.username == username))
        if user:
            return UserInDB(
                id=user.id,
                username=user.username,
                fullname=user.fullname,
                password_hash=user.password_hash,
                email=user.email    
            )
        raise EntityDoesNotExist(f"user with username {username} does not exist")
    
    async def get_user_by_email(self, email: str) -> UserInDB:
        user = await self.database.fetch_one(UserModel.select().where(UserModel.c.email == email))
        if user:
            return UserInDB(
                id=user.id,
                username=user.username,
                fullname=user.fullname,
                password_hash=user.password_hash,
                email=user.email    
            )
        raise EntityDoesNotExist(f"user with email {email} does not exist")

    async def create_user(self, user: UserRegister) -> None:
        while True:
            user_id = create_id_len_five()
            try: 
                await self.get_user_by_id(user_id)
                continue
            except EntityDoesNotExist:
                break

        await self.database.execute(UserModel.insert().values(
            id=user_id,
            username=user.username,
            fullname=user.fullname,
            password_hash=user.password,
            email=user.email   
        ))
    