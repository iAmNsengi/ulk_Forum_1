from django.urls import path
from .views import *
from django.contrib.auth.views import (
    LogoutView, 
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)

urlpatterns = [
    path("", Home, name="home"),
    path("login/", Login, name="login"),
    path("register/", Register, name="register"),
    path("logout/", Logout, name="logout"),
    path("update_profile/", Update_profile, name="update_profile"),
    path("profile/<str:username>/", User_profile, name="user profile"),
    path("profile/<str:username>/follow/", Follow_user, name="follow_ser"),
    path("post/<int:post_id>/", Post_detail, name="post"),
    path("post/<int:post_id>/like/", Post_like, name="post_like"),
    path("post/<int:post_id>/dislike/", Post_dislike, name="post_dislike"),
    path("post/<int:post_id>/delete/", Delete_post, name="post_delete"),
    path("explore/", Explore),
    path("activate/<uidb64>/<token>", activate, name="activate"),
    path('password-reset/', PasswordResetView.as_view(template_name='users/password_reset.html'),name='password-reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),name='password_reset_complete'),
]
