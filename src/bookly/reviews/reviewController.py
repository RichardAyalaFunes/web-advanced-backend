from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession

from bookly.auth.dependencies import get_current_user
from bookly.auth.userModel import User
from bookly.db.main import get_session
from bookly.reviews.reviewDto import ReviewCreateDTO
from bookly.reviews.reviewRepository import ReviewRepository
from bookly.reviews.service.createReview import CreateReviewService
from bookly.auth.userRepository import UserRepository
from bookly.book.BookRepository import BooksRepository

review_router = APIRouter()
review_repository = ReviewRepository()
user_repository = UserRepository()
book_repository = BooksRepository()
create_review_service = CreateReviewService(
    review_repository, user_repository, book_repository
)

@review_router.post("/book/{book_uid}")
async def add_review_to_book(
    book_uid: str, 
    review_data: ReviewCreateDTO,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    new_review = await create_review_service.execute(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid, 
        session=session
    )

    return new_review