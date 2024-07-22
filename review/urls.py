from django.urls import path

from review.views import CreateReviewView, UpdateReviewView


urlpatterns = [
    path('add/', CreateReviewView.as_view(), name='add_review'),
    path('update/<int:id>/', UpdateReviewView.as_view(), name='update_review'),
]
