from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.exceptions import HTTPException
from fastapi import status

from bookly.reviews.reviewDto import ReviewCreateDTO
from bookly.reviews.reviewRepository import ReviewRepository
from bookly.auth.userRepository import UserRepository
from bookly.book.BookRepository import BooksRepository


class CreateReviewService:
    def __init__(
        self,
        review_repository: ReviewRepository,
        user_repository: UserRepository,
        book_repository: BooksRepository,
    ):
        self.review_repository = review_repository
        self.user_repository = user_repository
        self.book_repository = book_repository

    async def execute(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateDTO,
        session: AsyncSession,
    ):
        """
        Add a new review to a book by a user.

        Args:
            user_email (str): The email address of the user leaving the review.
            book_uid (str): The unique identifier of the book being reviewed.
            review_data (ReviewCreateModel): The review data.
            session (AsyncSession): Database session used for committing.

        Returns:
            Review: The newly created review object.
        """
        try:
            book = await self.book_repository.get_book(book_uid=book_uid, session=session)
            if book is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Book not found."
                )

            user = await self.user_repository.get_user_by_email(
                email=user_email, session=session
            )
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
                )

            new_review = await self.review_repository.create_review(
                review_data=review_data,
                user=user,
                book=book,
                session=session,
            )

            return new_review

        except:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error in the database",
            )

