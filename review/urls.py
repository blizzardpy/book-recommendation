from django.urls import path

from review.views import CreateReviewView


urlpatterns = [
    path('add/', CreateReviewView.as_view(), name='add_review'),
]
