from django.urls import path
from suggest.views import SuggestBookView

urlpatterns = [
    path('', SuggestBookView.as_view(), name='suggest_book'),
]
