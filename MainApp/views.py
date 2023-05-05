from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

from datetime import date, datetime
import re
from itertools import chain
from django.views.generic import ListView
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from django.http import HttpResponse
from .tokens import account_activation_token
import random


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        user_profile = Profile.objects.get(user=user)

    except Exception as e:
        user = None

    if (
        user is not None
        and account_activation_token.check_token(user, token)
        and user_profile is not None
    ):
        user_profile.verified = True
        user_profile.save()
        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )
        return redirect("/")
    else:
        messages.error(request, "Activation link is invalid!")
    return redirect("/")


# Create your views here.
def Home(request):
    user_object = User.objects.filter(username=request.user).first()
    user_profile = Profile.objects.filter(user=user_object).first()

    user_following_list = []
    feed = []

    all_posts = Post.objects.filter(user=user_profile).all()
    feed.append(all_posts)

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    print(user_following)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        account = User.objects.get(username=usernames)
        profile = Profile.objects.get(user=account)
        feed_lists = Post.objects.filter(user=profile)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))

    # user suggestion startss
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [
        x for x in list(all_users) if (x not in list(user_following_all))
    ]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [
        x for x in list(new_suggestions_list) if (x not in list(current_user))
    ]
    random.shuffle(final_suggestions_list)

    print(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for user in final_suggestions_list:
        account = User.objects.get(username=user)
        profile_lists = Profile.objects.filter(user=account)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))[:5]

    form = PostForm()
    user = User.objects.filter(username=request.user).first()
    profile = Profile.objects.filter(user=user).first()

    if profile is not None:
        if profile.verified is False:
            logout(request)
            messages.info(
                request, f"Account not verified check your email  {profile.user.email}"
            )
            return redirect("/")

    context = {
        "posts": feed_list,
        "form": form,
        "profile": profile,
        "who_to_follow": suggestions_username_profile_list,
    }

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.info(request, "You must be logged in to post something!")
            return redirect("/")
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data["post"]
            try:
                user = User.objects.get(username=request.user)
                user_profile = Profile.objects.get(user=user)
                new_post = Post(user=user_profile, post=post)
                try:
                    new_post.save()
                    messages.info(request, "Posted successfully!")
                    return redirect("/")
                except:
                    messages.error(
                        request,
                        "An error occured while posting your data. Please try again!",
                    )
            except:
                messages.error(request, "User not found!")
        else:
            messages.info(request, "Invalid form!")
            return redirect("/")

    return render(request, "home.html", context)


class SearchResultsList(ListView):
    model = Post
    context_object_name = "post"
    paginate_by = 15
    template_name = "v2/search_result.html"

    def get_queryset(self):
        query = self.request.GET.get("q")
        return Post.objects.filter(Q(post__icontains=query))


@login_required(login_url="/")
def Post_detail(request, post_id):
    comments = Comment.objects.filter(post__id=post_id).all()
    context = {}
    try:
        post = Post.objects.get(id=post_id)
        form = PostForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data["post"]
            try:
                user = User.objects.get(username=request.user)
                new_comment = Comment(user=user, post=post, comment=comment)
                try:
                    new_comment.save()
                    new_comment = Comment.objects.get(
                        user=user, post=post, comment=comment
                    )
                    post.comments.add(new_comment)
                    post.save()
                    messages.info(request, "Comment posted successfully!")
                    return redirect(f"/post/{post_id}/")
                except Exception as e:
                    messages.error(request, e)
            except:
                messages.error(request, "User not found!")
        context = {
            "post": post,
            "form": form,
            "comments": comments,
        }
    except:
        messages.error(request, "Post not found!, It might have been deleted by user!")
        return redirect("/")
    profile = Profile.objects.filter(user=request.user).first()

    if profile is not None:
        if profile.verified is False:
            logout(request)
            messages.info(
                request, f"Account not verified check your email  {profile.user.email}"
            )
            return redirect("/")

    context = {
        "post": post,
        "form": form,
        "profile": profile,
        "comments": comments,
    }
    return render(request, "v2/post_detail.html", context)


@login_required(login_url="/")
def Post_like(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        user = User.objects.get(username=request.user)
        if not post.likes.contains(user):
            if post.dislikes.contains(user):
                post.likes.add(user)
                post.dislikes.remove(user)

            else:
                post.likes.add(user)

            try:
                post.save()
                return redirect(f"/post/{post_id}/")
            except Exception as e:
                messages.error(request, e)
                return redirect(f"/post/{post_id}/")

        return redirect(f"/post/{post_id}/")

    except Exception as e:
        messages.error(request, e)
        return redirect("/")


@login_required(login_url="/")
def Post_dislike(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
        user = User.objects.get(username=request.user)
        if not post.dislikes.contains(user):
            if post.likes.contains(user):
                post.likes.remove(user)
                post.dislikes.add(user)

            else:
                post.dislikes.add(user)

            try:
                post.save()
                return redirect(f"/post/{post_id}/")
            except Exception as e:
                messages.error(request, e)
                return redirect(f"/post/{post_id}/")

        return redirect(f"/post/{post_id}/")

    except:
        messages.error(request, "Post not found!")
        return redirect("/")


@login_required(login_url="/")
def Follow_user(request, username):
    user_to_follow = User.objects.get(username=username)
    follower = User.objects.get(username=request.user)

    action = FollowersCount.objects.filter(
        follower=follower, user=user_to_follow
    ).first()

    if action is not None:
        action.delete()
        return redirect(f"/profile/{username}/")
    else:
        action = FollowersCount(follower=follower, user=user_to_follow)
        action.save()
        return redirect(f"/profile/{username}/")


@login_required(login_url="/")
def User_profile(request, username):
    try:
        user = User.objects.get(username=username)
        me = User.objects.get(username=request.user)
        profile = Profile.objects.get(user=user)
        posts = Post.objects.filter(user=profile)

        my_followers = FollowersCount.objects.filter(user=request.user)
        my_following = FollowersCount.objects.filter(follower=request.user)

        isMyProfile = False
        amFollowing = False

        if request.user == profile.user:
            isMyProfile = True

        if FollowersCount.objects.filter(follower=me, user=user).first() is not None:
            amFollowing = True

        context = {
            "profile": profile,
            "isMyProfile": isMyProfile,
            "amFollowing": amFollowing,
            "posts": posts,
            "my_followers": my_followers,
            "my_following": my_following,
        }
        return render(request, "v2/profile.html", context)
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


@login_required(login_url="/")
def Delete_post(request, post_id):
    try:
        user = User.objects.get(username=request.user)
        user_profile = Profile.objects.get(user=user)
        try:
            delete_obj = Post.objects.get(id=post_id, user=user_profile)
            try:
                delete_obj.delete()
                messages.success(request, "Post deleted!")
                return redirect(f"/profile/{request.user}/")
            except Exception as e:
                messages.error(request, e)
                return redirect(f"/profile/{request.user}/")
        except:
            messages.error(
                request, "You are not the author of the post you want to delete!"
            )
    except Exception as e:
        messages.error(request, e)
        return redirect("/")


@login_required(login_url="/")
def Update_profile(request):
    profile = Profile.objects.filter(user=request.user).first() or None

    context = {
        "user_info": profile,
    }

    if not request.user.is_authenticated:
        messages.info(request, "You must be logged in!")
        return redirect("/")

    if request.method == "POST":
        full_name = request.POST["full_name"] or None
        dob = request.POST.get("dob") or None
        sex = request.POST.get("sex") or None
        phone = request.POST.get("phone") or None
        website = request.POST["website"] or None
        bio = request.POST["bio"] or None
        location = request.POST["location"] or None
        avatar = request.FILES.get("image") or None

        today = date.today()

        try:
            profile = Profile.objects.get(user=request.user)
            if full_name is not None:
                if not re.match(
                    "^([a-zA-Z]{2,}\s[a-zA-Z]{1,}'?-?[a-zA-Z]{2,}\s?([a-zA-Z]{1,})?)",
                    full_name,
                ):
                    messages.error(request, "Invalid Name!")
                    return redirect("/update_profile/")
                profile.name = full_name
            if dob is not None:
                dob = datetime.strptime(dob, "%Y-%m-%d")
                age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )
                print(age)
                if age < 18:
                    messages.error(
                        request, "Software not intended to people under 18 years!"
                    )
                    return redirect("/update_profile/")
                profile.dob = dob
            if sex is not None:
                profile.sex = sex
            if phone is not None:
                if not re.match(
                    "^(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}$", phone
                ):
                    messages.error(request, "Invalid Phone number!")
                    return redirect("/update_profile/")
                profile.phone = phone
            if location is not None:
                if not re.match(
                    "^([a-zA-Z\u0080-\u024F]+(?:. |-| |'))*[a-zA-Z\u0080-\u024F]*$",
                    location,
                ):
                    messages.error(request, "Invalid city name!")
                    return redirect("/update_profile/")
                profile.location = location
            if website is not None:
                profile.website = website
            if bio is not None:
                profile.bio = bio
            if not avatar is None:
                profile.avatar = avatar
            profile.save()
            messages.info(request, "Updated successfully!")
            return redirect(f"/update_profile/")

        except Exception as e:
            messages.info(request, e)

    return render(request, "v2/update_profile.html", context)


@login_required(login_url="/")
def Explore(request):
    user_object = User.objects.filter(username=request.user).first()
    user_profile = Profile.objects.filter(user=user_object).first()

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    print(user_following)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        account = User.objects.get(username=usernames)
        profile = Profile.objects.get(user=account)
        feed_lists = Post.objects.filter(user=profile)
        feed.append(feed_lists)

    all_posts = Post.objects.filter(user=user_profile).all()
    feed.append(all_posts)

    feed_list = list(chain(*feed))

    # user suggestion startss
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [
        x for x in list(all_users) if (x not in list(user_following_all))
    ]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestions_list = [
        x for x in list(new_suggestions_list) if (x not in list(current_user))
    ]
    random.shuffle(final_suggestions_list)

    print(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for user in final_suggestions_list:
        account = User.objects.get(username=user)
        profile_lists = Profile.objects.filter(user=account)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    context = {
        "posts": feed_list,
        "who_to_follow": suggestions_username_profile_list,
    }
    return render(request, "v2/explore.html", context)


def Login(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                the_user = User.objects.get(username=username)
                profile = Profile.objects.filter(user=the_user).first()
                if profile.verified is False:
                    return render(request, "verify.html")
                login(request, user)
                return redirect("/")
            else:
                messages.error(request, "User not found, please try again!")
                return redirect("/")

        except Exception as e:
            messages.error(request, e)
            return redirect("/")

    return redirect("/")


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string(
        "template_activate_account.html",
        {
            "user": user.username,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(
            request,
            f"Dear {user}, please go to you email {to_email} inbox and click on \
            received activation link to confirm and complete the registration. Note: Check your spam folder.",
        )
    else:
        messages.error(
            request,
            f"Problem sending confirmation email to {to_email}, check if you typed it correctly.",
        )


def resetPassword(request):
    if request.method == "POST":
        to_email = request.POST.get("email")

        try:
            user = User.objects.get(email=to_email)
        except Exception as e:
            messages.error(request, e)
            return redirect("/")

        mail_subject = "Reset your password."
        message = render_to_string(
            "template_reset_password.html",
            {
                "user": user.username,
                "password": user.password,
                "domain": get_current_site(request).domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
                "protocol": "https" if request.is_secure() else "http",
            },
        )
        email = EmailMessage(mail_subject, message, to=[to_email])
        if email.send():
            messages.success(request, f"Check your email for reset link!")
            return redirect("/")
        else:
            messages.error(
                request,
                f"Problem sending confirmation email to {to_email}, check if you typed it correctly.",
            )
            return redirect("/")


def Register(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        err = False

        if password1 != password2:
            messages.error(request, "Password donot match!")
            err = True
        try:
            User.objects.get(username=username)
            err = True
            messages.error(request, "User exists, please try to register again!")
        except:
            if err == False:
                user = User.objects.create_user(
                    username=username, email=email, password=password1
                )
                try:
                    user.save()
                    activateEmail(request, user, email)
                    user_profile = Profile(user=user)
                    user_profile.save()
                    messages.success(request, "User created successfully!")
                except Exception as e:
                    messages.error(request, e)

        context = {
            "error": err or None,
        }
    context = {}
    return render(request, "home.html", context)


def Logout(request):
    logout(request)
    return redirect("/")
