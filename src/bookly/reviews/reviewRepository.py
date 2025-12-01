from sqlalchemy.ext.asyncio import AsyncSession

from bookly.reviews.reviewModel import Review
from bookly.reviews.reviewDto import ReviewCreateDTO
from bookly.auth.userModel import User
from bookly.book.BookModel import Book


class ReviewRepository:
    async def create_review(
        self,
        review_data: ReviewCreateDTO,
        user: User,
        book: Book,
        session: AsyncSession,
    ) -> Review:
        """
        Add a new review to a book by a user.

        Args:
            review_data (ReviewCreateModel): The review data.
            user (User): The user leaving the review.
            book (Book): The book being reviewed.
            session (AsyncSession): Database session used for committing.

        Returns:
            Review: The newly created review object.
        """
        review_data_dict = review_data.model_dump()

        new_review = Review(**review_data_dict)
        new_review.book = book
        new_review.user = user

        session.add(new_review)
        await session.commit()
        await session.refresh(new_review)

        return new_review
