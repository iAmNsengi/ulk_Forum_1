from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import MessageForm

from .models import Room, Message
from django.contrib.auth.decorators import login_required


@login_required(login_url="/")
def index_view(request):
    user = User.objects.get(username=request.user)

    if request.method == "POST":
        room_name = request.POST.get("room")
        room_key = request.POST.get("key")

        try:
            room = Room.objects.get(name=room_name, key=room_key)
            if not room.members.contains(user):
                room.members.add(user)
            return redirect(f"/chat/{room_name}/")
        except Exception as e:
            messages.error(request, e)
            return redirect("/chat/")

    return render(
        request,
        "index2.html",
        {
            "rooms": Room.objects.filter(members=user),
        },
    )


@login_required(login_url="/")
def create_room(request):
    user = User.objects.get(username=request.user)
    if request.method == "POST":
        room_name = request.POST.get("new-room-name")
        room_key = request.POST.get("new-room-key")

        try:
            Room.objects.get(name=room_name, key=room_key)
            messages.info(request, "Room exists")
            return redirect(f"/chat/")
        except Exception as e:
            new_room = Room(name=room_name, admin=user, key=room_key)
            try:
                new_room.save()
                new_room.members.add(user)
                new_room.save()
                messages.info(
                    request, "Room created successfully, Now you can login in the Room!"
                )
                return redirect("/chat/")
            except Exception as e:
                messages.erro(request, e)
                return redirect("/chat/")

    return render(
        request,
        "index.html",
        {
            "rooms": Room.objects.all(),
        },
    )


@login_required(login_url="/")
def room_view(request, room_name):
    user = User.objects.get(username=request.user)
    form = MessageForm()
    context = {}
    is_my_room = False

    try:
        chat_room = Room.objects.get(name=room_name)
        if chat_room.admin == user:
            is_my_room = True
        if chat_room.members.contains(user):
            message = Message.objects.filter(room=chat_room).all() or None
            context = {
                "room": chat_room,
                "messages": message,
                "form": form,
                "is_my_room": is_my_room,
            }
        else:
            messages.error(request, "You are not allowed to enter the room")
            return redirect("/chat/")
    except:
        messages.error(
            request, "An error occured try to get room info, please try again!"
        )
        return redirect("/chat/")
    return render(request, "room2.html", context)


@login_required(login_url="/")
def delete_room(request, id):
    user = User.objects.get(username=request.user)
    try:
        room = Room.objects.get(id=id)
        if room.admin == user:
            room.delete()
            messages.info(request, "Room deleted successfully!")
            return redirect("/chat/")
    except Exception as e:
        messages.error(request, e)
        return redirect("/chat/")

    return redirect("/chat/")
