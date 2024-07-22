from django.db import models
from authentication.models import User
from book.models import Book
from django.core.validators import MaxValueValidator, MinValueValidator


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        db_table = 'reviews'
        unique_together = ('book', 'user')

    def __str__(self):
        return f'Review by {self.user} for {self.book} with rating {self.rating}'
