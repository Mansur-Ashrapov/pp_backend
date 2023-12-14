import asyncio
import base64

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError

from app.db.exceptions import EntityDoesNotExist
from app.api.dependecies.database import get_repository
from app.api.dependecies.auth import get_oauth2

from app.models.schemas.auth import Token
from app.models.schemas.student import Student, StudentIn
from app.models.schemas.test import Test, TestIn
from app.models.schemas.testresult import TestResult
from app.models.schemas.classroom import Class, ClassIn, ClassOut
from app.models.schemas.users import User

from app.db.repositories.classroom import ClassRepository
from app.db.repositories.student import StudentRepository
from app.db.repositories.test import TestRepository
from app.db.repositories.testresult import TestResultRepository
from app.db.repositories.users import UserRepository

from app.services.security import get_password_hash, get_user_from_payload

import numpy as np
import cv2


router = APIRouter()


@router.post('/')
async def recognize_test(
        file: UploadFile = File(),
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository))
    ):
    try:
        await get_user_from_payload(token, users_repo)

        contents = await file.read()
        nparr = np.fromstring(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        cv2.imshow('im', img)
        return ['A', 'B', 'C', 'D']
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)