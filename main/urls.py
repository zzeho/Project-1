from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup, name="signup"),
    path("reviews/create/", views.create_review, name="create_review"),
    path("logout/", views.logout_page, name="logout"),
    path("reviews/<int:review_id>/delete/", views.delete_review, name="delete_review"),
    ]