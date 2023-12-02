from uuid import UUID, uuid4

from .models import Rating


class RatingService:
    mock_db: dict[UUID, Rating] = {}

    async def set_rating(self, rating: Rating) -> Rating:
        """
        Set the rating for a specific model and save it to the database.

        :param rating: The rating to be set.
        :type rating: Rating
        :return: The saved rating.
        :rtype: Rating
        """
        rating_id = rating.id if rating.id else uuid4()
        self.mock_db[rating_id] = rating.model_copy(update={'id': rating_id})
        return self.mock_db[rating_id]

    async def get_ratings(self, question_id: UUID) -> list[Rating]:
        """
        Get the list of ratings for a given question ID.

        :param question_id: The unique ID of the question.
        :type question_id: UUID
        :return: The list of ratings for the question.
        :rtype: list[Rating]
        """
        return [*filter(lambda x: x.question_id == question_id, self.mock_db.values())]