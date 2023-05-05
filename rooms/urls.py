from django.urls import path

from . import views

urlpatterns = [
    path("", views.index_view, name="chat-index"),
    path("create/", views.create_room, name="create_chat_room"),
    path("<str:room_name>/", views.room_view, name="chat-room"),
    path("delete/<int:id>/", views.delete_room),
]
