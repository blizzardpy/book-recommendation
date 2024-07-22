from django.urls import path
from book.views import BookListView, BooksListByGenreView


urlpatterns = [
    path('', BooksListByGenreView.as_view(), name='book_by_genre'),
    path('list/', BookListView.as_view(), name='book_list'),
]
