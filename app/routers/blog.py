from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime
from typing import Annotated
from pymongo import ReturnDocument

from app.cores.database import db
from app.schema.user import User
from app.schema.blog import Blog, BlogUpdate
from app.schema.response import SuccessResponse, ErrorResponse
from app.services.user import get_current_user

router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponse
)
async def create_blog(
    blog: Blog,
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        blog_dict = blog.model_dump()
        blog_dict['author_id'] = str(current_user['_id'])
        blog_dict['created_at'] = datetime.now()
        blog_dict['updated_at'] = datetime.now()
        result = await db.blogs.insert_one(blog_dict)

        await db.users.update_one(
            {"_id": ObjectId(blog_dict['author_id'])},
            {"$push": {"blogs": str(result.inserted_id)}}
        )

        return SuccessResponse(
            status="Success",
            message="Blog created successfully!",
            data={"id": str(result.inserted_id)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="Error",
                message=str(e)
            ).model_dump()
        )


@router.put("/{blog_id}", response_model=SuccessResponse)
async def update_blog(
    blog_id: str,
    blog_update: BlogUpdate,
    current_user: User = Depends(get_current_user)
):
    try:
        blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
        if not blog:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    status="Error",
                    message="Blog not found"
                ).model_dump()
            )

        if str(blog['author_id']) != str(current_user['_id']):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    status="Error",
                    message="You are not authorized to update this blog"
                ).model_dump()
            )
        blog_dict = blog_update.model_dump(exclude_unset=True)
        blog_dict['updated_at'] = datetime.now()
        result = await db.blogs.find_one_and_update(
            {"_id": ObjectId(blog_id)},
            {"$set": blog_dict},
            return_document=ReturnDocument.AFTER
        )
        result['id'] = str(result.pop('_id'))

        return SuccessResponse(
            status="Success",
            message="Blog updated successfully!",
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


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: str,
    current_user: User = Depends(get_current_user)
):
    try:
        blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
        if not blog:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=ErrorResponse(
                    status="Error",
                    message="Blog not found"
                ).model_dump()
            )

        if str(blog['author_id']) != str(current_user['_id']):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content=ErrorResponse(
                    status="Error",
                    message="You are not authorized to delete this blog"
                ).model_dump()
            )

        await db.blogs.delete_one({"_id": ObjectId(blog_id)})

        await db.users.update_one(
            {"_id": ObjectId(current_user['_id'])},
            {"$pull": {"blog_ids": ObjectId(blog_id)}}
        )

        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content="User deleted successfully!"
        )
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                status="Error",
                message=str(e)
            ).model_dump()
        )
