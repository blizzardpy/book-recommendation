from django.urls import path
from api.views import LoginView, BookListView, BooksListByGenreView
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('book/list/', BookListView.as_view(), name='book_list'),
    path('book/', BooksListByGenreView.as_view(), name='book_by_genre'),
]
