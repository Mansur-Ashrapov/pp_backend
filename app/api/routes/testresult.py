import asyncio
import cv2 
import numpy as np
import base64

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from asyncpg.exceptions import UndefinedObjectError, UniqueViolationError, ForeignKeyViolationError

from app.db.exceptions import EntityDoesNotExist
from app.api.dependecies.database import get_repository
from app.api.dependecies.auth import get_oauth2

from app.models.schemas.auth import Token
from app.models.schemas.student import Student, StudentIn
from app.models.schemas.test import Test, TestIn
from app.models.schemas.testresult import TestResult, TestBlank
from app.models.schemas.classroom import Class, ClassIn, ClassOut
from app.models.schemas.users import User

from app.db.repositories.classroom import ClassRepository
from app.db.repositories.student import StudentRepository
from app.db.repositories.test import TestRepository
from app.db.repositories.testresult import TestResultRepository
from app.db.repositories.users import UserRepository

from app.omr import omr

from app.services.security import get_password_hash, get_user_from_payload

router = APIRouter()


@router.post("/", response_model=TestResult)
async def recognize_test_and_create_result(
        file: UploadFile = File(...),
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        testresult_repo: TestResultRepository = Depends(get_repository(TestResultRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))):
    """Получить результаты теста по фото, результаты сами запишутся в БД"""
    try:
        user = await get_user_from_payload(token, users_repo)

        contents = await file.read()
        nparr = np.fromstring(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        testres_data: TestResult = omr.recognize_test(img)

        # _, encoded_img = cv2.imencode('.PNG', img)
        # encoded_img = base64.b64encode(encoded_img)


        test_data = TestResult(
            test_id=testres_data.id,
            student_id=testres_data.student_id,
            class_id=testres_data.class_id,
            score=100,
            answers=[]
        )
        
        await testresult_repo.create_test(test_data)

        return test_data
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForeignKeyViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Видимо не правильно считался код")
    
@router.get("/")
async def get_blank_test(
        blank_data: TestBlank,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))):
    """Получить бланк теста для определенного класса"""
    try:
        await get_user_from_payload(token, users_repo)
        _, encoded_img = cv2.imencode('.PNG', 'dsa')
        encoded_img = base64.b64encode(encoded_img)
        return {'dimensions': encoded_img, "encoded_img": encoded_img}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)