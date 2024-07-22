from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    genre = models.CharField(max_length=50)

    class Meta:
        db_table = 'books'
        unique_together = ('title', 'author', 'genre')

    def __str__(self):
        return f'{self.title} by {self.author}'
