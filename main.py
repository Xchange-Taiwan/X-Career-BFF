import os
from mangum import Mangum
from fastapi import FastAPI, Request, \
    Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException, \
    Depends, \
    APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.infra.databse import SessionLocal
from src.router.v1 import (
    auth,
    user,
    mentor,
    search,
)
from src.config import exception

STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'
app = FastAPI(title='X-Career: BFF', root_path=root_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


# Middleware to handle transaction rollback on exceptions
@app.middleware("http")
async def rollback_on_exception(request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        # Rollback the database session on any unhandled exception
        db = SessionLocal()
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


router_v1 = APIRouter(prefix='/api/v1')
router_v1.include_router(auth.router)
router_v1.include_router(user.router)
router_v1.include_router(mentor.router)
router_v1.include_router(search.router)

app.include_router(router_v1)

exception.include_app(app)


@app.get('/gateway/{term}')
async def info(term: str):
    if term != 'yolo':
        raise HTTPException(
            status_code=418, detail='Oops! Wrong phrase. Guess again?')
    return JSONResponse(content={'mention': 'You only live once.'})


# Mangum Handler, this is so important
handler = Mangum(app)
