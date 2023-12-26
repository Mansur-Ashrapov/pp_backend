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

from app.models.schemas.testresult import TestResult, TestBlank

from app.db.repositories.classroom import ClassRepository
from app.db.repositories.test import TestRepository
from app.db.repositories.testresult import TestResultRepository
from app.db.repositories.users import UserRepository

from app.omr import omr, create_test_sheets

from app.services.security import get_user_from_payload

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
        await get_user_from_payload(token, users_repo)

        contents = await file.read()
        nparr = np.fromstring(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        result = omr.recognize_test(img)

        test = await test_repo.get_test_by_id(result.test_id)

        def get_score(answers1, answers2):
            count = len(answers1)
            res = [1 for i, j in zip(answers1, answers2) if i == j]
            return int((len(res)/count)*100)

        to_db = TestResult(
            test_id=result.test_id,
            student_id=result.student_id,
            class_id=result.class_id,
            score=get_score(result.answers, test.answers),
            answers=result.answers
        )
        await testresult_repo.create_test(to_db)
        return to_db
    
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForeignKeyViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Видимо не правильно считался код")
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    

@router.post("/get_sheet")
async def get_blank_test(
        blank_data: TestBlank,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))):
    """Получить бланк теста для определенного класса"""
    try:
        await get_user_from_payload(token, users_repo)
        await class_repo.get_class_by_id(blank_data.class_id)
        await test_repo.get_test_by_id(blank_data.test_id)

        data = ' '.join([str(blank_data.class_id), str(blank_data.test_id)]) 
        img = create_test_sheets.get_sheet_with_qr(data)

        _, encoded_img = cv2.imencode('.PNG', img)
        encoded_img = base64.b64encode(encoded_img)
        return {'encoded_img': encoded_img}
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])