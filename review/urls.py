from django.urls import path

from review.views import CreateReviewView, UpdateReviewView, DestroyReviewView, UserReviewsView


urlpatterns = [
    path('list', UserReviewsView.as_view(), name='user_reviews'),
    path('add/', CreateReviewView.as_view(), name='add_review'),
    path('update/<int:id>/', UpdateReviewView.as_view(), name='update_review'),
    path('delete/<int:id>/', DestroyReviewView.as_view(), name='delete_review'),
]
