from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Annotated
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.cores.database import db
from app.schema.user import User, UserUpdate, Token
from app.schema.response import SuccessResponse, ErrorResponse
from app.cores.config import settings
from app.cores.security import verify_password
from app.services.user import create_access_token, get_current_user, clean_user

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponse
)
async def create_user(user: User):
    try:
        user_dict = user.model_dump()
        user_dict = clean_user(user_dict)
        result = await db.users.insert_one(user_dict)
        return SuccessResponse(
            status="Success",
            message="User created successfully!",
            data={"id": str(result.inserted_id)}
        )
    except DuplicateKeyError:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ErrorResponse(
                status="Error",
                message="Email already registered"
            ).model_dump()
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="Error",
                message=str(e)
            ).model_dump()
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = await db.users.find_one({"email": form_data.username})
    if not user:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                status="Error",
                message="User not found"
            ).model_dump()
        )
    if not verify_password(form_data.password, user['password']):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(
                status="Error",
                message="Incorrect credentials"
            ).model_dump()
        )
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": user['email']}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )


@router.get("/", response_model=SuccessResponse)
async def list_users():
    try:
        users = await db.users.find().to_list(length=None)
        final_users = []
        for user in users:
            user['id'] = str(user.pop('_id'))
            user.pop('password', None)
            final_users.append(user)
        return SuccessResponse(
            status="Success",
            message="Users retrieved successfully!",
            data=final_users
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="Error",
                message=str(e)
            ).model_dump()
        )


@router.get("/blogs", response_model=SuccessResponse)
async def get_user_blogs(
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        blog_ids = list(map(ObjectId, current_user.get("blogs", [])))
        if not blog_ids:
            return SuccessResponse(
                status="Success",
                message="No blogs found for this user",
                data=[]
            )

        blogs_cursor = db.blogs.find({"_id": {"$in": blog_ids}})
        blogs = await blogs_cursor.to_list(length=None)
        print(blogs)
        for blog in blogs:
            blog['id'] = str(blog.pop('_id'))

        return SuccessResponse(
            status="Success",
            message="Blogs retrieved successfully!",
            data=blogs
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="Error",
                message=str(e)
            ).model_dump()
        )


@router.put("/{user_id}", response_model=SuccessResponse)
async def update_user(user_id: str, user: UserUpdate):
    try:
        data = user.model_dump(exclude_unset=True)
        data['updated_at'] = datetime.now()
        result = await db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": data},
            return_document=ReturnDocument.AFTER
        )
        if not result:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    status="Error",
                    message="User not found"
                ).model_dump()
            )
        result['id'] = str(result.pop('_id'))
        result.pop('password', None)
        return SuccessResponse(
            status="Success",
            message="User updated successfully!",
            data=result
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="Error",
                message=str(e)
            ).model_dump()
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    try:
        result = await db.users.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    status="Error",
                    message="User not found"
                ).model_dump()
            )
        return SuccessResponse(
            status="Success",
            message="User deleted successfully!"
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="Error",
                message=str(e)
            ).model_dump()
        )
