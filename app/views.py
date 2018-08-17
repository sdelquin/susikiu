import random
import json
import uuid
import operator
import functools

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as dj_login
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout as dj_logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse

from .forms import LoginForm
from .forms import RegisterForm
from .forms import RemindCredentialsForm
from .forms import ResetPasswordForm
from .forms import ProfileForm
from .models import DifficultyLevel
from .models import DancingLevel
from .models import DancingStyle
from .models import EndUser
from .tasks import send_confirmation_account_email
from .tasks import send_remind_credentials_email
from .models import Video


def index(request):
    return render(
        request,
        "app/index.html",
        {
            "index": True,
            "bgvideo_id": settings.BGVIDEO_ID,
            "num_videos": len(Video.objects.all()),
            "num_users": len(EndUser.objects.all())
        }
    )


def login(request):
    if request.user.is_authenticated():
        return redirect("videos")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username,
                                password=password)
            if user is not None:
                if user.is_active:
                    dj_login(request, user)
                    next_url = request.GET.get("next", "videos")
                    return redirect(next_url)
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Su cuenta ha sido deshabilitada. "
                        "Contacte con el responsable de la aplicación."
                    )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Credenciales incorrectas."
                )
            return render(
                request,
                "app/message.html",
                {"url_next": reverse("login")}
            )
    else:
        form = LoginForm()
    return render(
        request,
        "app/login.html",
        {"form": form}
    )


def logout(request):
    dj_logout(request)
    return redirect("login")


def register(request):
    if request.user.is_authenticated():
        return redirect("videos")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            id = uuid.uuid1()
            redis_key = "register_{}".format(id)
            settings.REDIS.set(redis_key, json.dumps(form.cleaned_data))
            send_confirmation_account_email.delay(
                form.cleaned_data.get("first_name"),
                "http://susikiu.es/register/{}/".format(id),
                form.cleaned_data.get("email")
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                "Se ha enviado un correo electrónico a la dirección "
                "proporcionada. "
                "Revisa tu bandeja de entrada (incluido Spam) para confirmar "
                "la cuenta."
            )
            return render(
                request,
                "app/message.html"
            )
    else:
        form = RegisterForm()
    return render(
        request,
        "app/register.html",
        {"form": form}
    )


@transaction.atomic
def confirm_register(request, confirmation_id):
    if request.user.is_authenticated():
        return redirect("videos")

    redis_key = "register_{}".format(confirmation_id)
    if not settings.REDIS.exists(redis_key):
        messages.add_message(
            request,
            messages.ERROR,
            "Identificador de registro no encontrado."
        )
        url_next = reverse("register")
    else:
        data = json.loads(settings.REDIS.get(redis_key))
        user = User(
            username=data["username"],
            email=data["email"],
            first_name=data["first_name"],
            last_name=data["last_name"]
        )
        user.set_password(data["password"])
        user.save()
        enduser = EndUser(user=user)
        enduser.save()

        settings.REDIS.delete(redis_key)

        messages.add_message(
            request,
            messages.SUCCESS,
            "Enhorabuena. Tu cuenta ha sido creada satisfactoriamente. "
        )
        url_next = reverse("login")

    return render(
        request,
        "app/message.html",
        {"url_next": url_next}
    )


def remind_credentials(request):
    if request.user.is_authenticated():
        return redirect("videos")

    if request.method == "POST":
        form = RemindCredentialsForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            # validation already checked that user exists
            u = User.objects.get(email=email)
            id = uuid.uuid1()
            redis_key = "reset_{}".format(id)
            settings.REDIS.set(redis_key, u.username)
            send_remind_credentials_email.delay(
                u.username,
                "http://susikiu.es/reset_password/{}/".format(id),
                email
            )
            messages.add_message(
                request,
                messages.SUCCESS,
                "Se ha enviado un correo electrónico a la dirección "
                "proporcionada. "
                "Revisa tu bandeja de entrada (incluido Spam) para resetear "
                "la contraseña."
            )
            return render(
                request,
                "app/message.html"
            )
    else:
        form = RemindCredentialsForm()

    return render(
        request,
        "app/remind_credentials.html",
        {"form": form}
    )


def reset_password(request, reset_id):
    if request.user.is_authenticated():
        return redirect("videos")

    redis_key = "reset_{}".format(reset_id)
    if not settings.REDIS.exists(redis_key):
        messages.add_message(
            request,
            messages.ERROR,
            "Identificador de reseteo de contraseña no encontrado."
        )
        url_next = reverse("login")
        return render(
            request,
            "app/message.html",
            {"url_next": url_next}
        )
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get("password")
            username = settings.REDIS.get(redis_key)
            u = User.objects.get(username=username)
            u.set_password(password)
            u.save()
            messages.add_message(
                request,
                messages.SUCCESS,
                "La contraseña ha sido reestablecida con éxito."
            )
            settings.REDIS.delete(redis_key)
            return render(
                request,
                "app/message.html",
                {"url_next": reverse("login")}
            )
    else:
        form = ResetPasswordForm()

    return render(
        request,
        "app/reset_password.html",
        {"form": form}
    )


@login_required
def videos(request):
    if not request.user.is_superuser:
        enduser = EndUser.objects.get(user=request.user)
        if not enduser.complete_profile() and random.randint(1, 5) == 1:
            messages.add_message(
                request,
                messages.INFO,
                "Anímate a completar tu perfil. Mola mucho!"
            )
    request.session["filtered_video_ids"] = ""
    return render(
        request,
        "app/videos.html",
        {
            "videos": Video.objects.all().order_by("-recorded", "title"),
            "show_msg_close_button": True,
            "url_next": reverse("edit_profile")
        }
    )


@login_required
def video(request, video_id):
    filtered_video_ids = request.session.get("filtered_video_ids", "")
    if filtered_video_ids:
        videos = [Video.objects.get(pk=id) for id in filtered_video_ids]
    else:
        videos = Video.objects.all().order_by("-recorded", "title")

    try:
        v = Video.objects.get(pk=video_id)
    except Video.DoesNotExist:
        messages.add_message(
            request,
            messages.ERROR,
            "El vídeo al que está intentando acceder no existe."
        )
        return render(
            request,
            "app/message.html",
            {"url_next": reverse("videos")}
        )

    previous_video_id, next_video_id = v.get_siblings_video_ids(videos)

    if request.user.is_superuser:
        already_liked = False
    else:
        v.views_count += 1
        v.save()
        enduser = EndUser.objects.get(user=request.user)
        already_liked = len(enduser.video_set.filter(id=video_id)) > 0
    return render(
        request,
        "app/video.html",
        {
            "video": v,
            "already_liked": already_liked,
            "previous_video_id": previous_video_id,
            "next_video_id": next_video_id,
            "video_likes": v.likes.all().order_by("user__first_name",
                                                  "user__last_name")
        }
    )


@login_required
@transaction.atomic
def video_affinity(request, video_id, affinity):
    v = Video.objects.get(pk=video_id)
    enduser = EndUser.objects.get(user=request.user)
    if affinity == "like":
        if not v.likes.filter(id=enduser.id):
            v.likes.add(enduser)
            v.likes_count += 1
    else:
        if v.likes.filter(id=enduser.id):
            v.likes.remove(enduser)
            v.likes_count -= 1
    v.save()
    likes = v.likes.all().order_by("user__first_name", "user__last_name")
    r = {
        "count": v.likes_count,
        "likes": [l.get_fullname() for l in likes]
    }
    return HttpResponse(json.dumps(r))


@login_required
def filter_videos(request,
                  dancing_level_id,
                  dancing_style_id,
                  difficulty_level_id,
                  order_criteria,
                  order_key,
                  my_likes,
                  search):

    if dancing_level_id == "!":
        dancing_level_ids = DancingLevel.objects.values_list(
            "id",
            flat=True
        )
    else:
        dancing_level_ids = [dancing_level_id]

    if dancing_style_id == "!":
        dancing_style_ids = DancingStyle.objects.values_list(
            "id",
            flat=True
        )
    else:
        dancing_style_ids = [dancing_style_id]

    if difficulty_level_id == "!":
        difficulty_level_ids = DifficultyLevel.objects.values_list(
            "id",
            flat=True
        )
    else:
        difficulty_level_ids = [difficulty_level_id]

    if order_key == "!":
        order_by_field = "-recorded"
    else:
        if order_criteria == "+":
            oc = ""
        else:
            oc = order_criteria
        if order_key == "d":
            order_by_field = "{}recorded".format(oc)
        elif order_key == "l":
            order_by_field = "{}likes_count".format(oc)
        elif order_key == "v":
            order_by_field = "{}views_count".format(oc)
        elif order_key == "t":
            order_by_field = "{}duration".format(oc)

    search_pieces = search.split()
    if not search_pieces:
        search_pieces = [""]

    videos = Video.objects.filter(
        functools.reduce(
            operator.or_,
            (Q(title__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(dancer1__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(dancer2__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(song__title__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(song__artist__icontains=s) for s in search_pieces)),
        dancing_level__id__in=dancing_level_ids,
        dancing_style__id__in=dancing_style_ids,
        difficulty_level__id__in=difficulty_level_ids
    ).order_by(order_by_field, "title")

    if my_likes == "my":
        enduser = EndUser.objects.get(user=request.user)
        videos = videos.filter(likes=enduser).order_by(order_by_field, "title")

    request.session["filtered_video_ids"] = [v.id for v in videos]

    return render(
        request,
        "app/videos.html",
        {
            "selected_dancing_level_id": dancing_level_id,
            "selected_dancing_style_id": dancing_style_id,
            "selected_difficulty_level_id": difficulty_level_id,
            "selected_order_criteria": order_criteria,
            "inverted_order_criteria": "+" if order_criteria == "-" else "-",
            "selected_order_key": order_key,
            "selected_search": search,
            "selected_my_likes": my_likes,
            "videos": videos
        }
    )


def forbidden(request):
    return render(request, "app/403.html")


def page_not_found(request):
    return render(request, "app/404.html")


def server_error(request):
    return render(request, "app/500.html")


@login_required
def edit_profile(request):
    enduser = EndUser.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.username = form.cleaned_data["username"]
            user.email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            if password:
                user.set_password(password)
            dancing_level_code = form.cleaned_data["dancing_level"]
            if dancing_level_code:
                enduser.dancing_level = \
                    DancingLevel.objects.get(code=dancing_level_code)
            else:
                enduser.dancing_level = None
            favourite_dancing_style_code = \
                form.cleaned_data["favourite_dancing_style"]
            if favourite_dancing_style_code:
                enduser.favourite_dancing_style = \
                    DancingStyle.objects.get(code=favourite_dancing_style_code)
            else:
                enduser.dancing_level = None
            enduser.teacher = form.cleaned_data["teacher"]
            avatar = form.cleaned_data["avatar"]
            if avatar is not None:
                if avatar is False:
                    enduser.avatar = None
                else:
                    enduser.avatar = avatar
            enduser.date_of_birth = form.cleaned_data["date_of_birth"]
            enduser.why_dance = form.cleaned_data["why_dance"]
            enduser.bio = form.cleaned_data["bio"]
            enduser.twitter_username = \
                form.cleaned_data["twitter_username"]
            enduser.facebook_username = \
                form.cleaned_data["facebook_username"]
            enduser.snapchat_username = \
                form.cleaned_data["snapchat_username"]
            enduser.instagram_username = \
                form.cleaned_data["instagram_username"]

            user.save()
            enduser.user = user
            enduser.save()

            messages.add_message(
                request,
                messages.SUCCESS,
                "Tus datos de perfil se han modificado satisfactoriamente."
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Hay errores en el formulario. Revisa los campos introducidos."
            )
    else:
        form = ProfileForm(
            initial={
                "first_name": enduser.user.first_name,
                "last_name": enduser.user.last_name,
                "username": enduser.user.username,
                "email": enduser.user.email,
                "dancing_level": enduser.get_dancing_level_code(),
                "favourite_dancing_style":
                    enduser.get_favourite_dancing_style_code(),
                "teacher": enduser.teacher,
                "avatar": enduser.avatar,
                "date_of_birth": enduser.date_of_birth,
                "why_dance": enduser.why_dance,
                "bio": enduser.bio,
                "twitter_username": enduser.twitter_username,
                "facebook_username": enduser.facebook_username,
                "snapchat_username": enduser.snapchat_username,
                "instagram_username": enduser.instagram_username
            }
        )
    return render(
        request,
        "app/edit_profile.html",
        {
            "form": form,
            "show_msg_close_button": True
        }
    )


@login_required
def users(request):
    endusers = EndUser.objects.all().order_by("user__first_name")
    return render(
        request,
        "app/users.html",
        {"endusers": endusers}
    )


@login_required
def filter_users(request,
                 dancing_level_id,
                 dancing_style_id,
                 order_criteria,
                 order_key,
                 search):

    if order_key == "!":
        order_by_field = "user__first_name"
    else:
        if order_criteria == "+":
            oc = ""
        else:
            oc = order_criteria
        if order_key == "n":
            order_by_field = "{}user__first_name".format(oc)
        elif order_key == "b":
            order_by_field = "{}date_of_birth".format(oc)
        elif order_key == "j":
            order_by_field = "{}user__date_joined".format(oc)

    search_pieces = search.split()
    if not search_pieces:
        search_pieces = [""]

    endusers = EndUser.objects.filter(
        functools.reduce(
            operator.or_,
            (Q(user__first_name__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(user__last_name__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(user__username__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(twitter_username__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(facebook_username__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(snapchat_username__icontains=s) for s in search_pieces)) |
        functools.reduce(
            operator.or_,
            (Q(instagram_username__icontains=s) for s in search_pieces))
    )

    if dancing_level_id != "!":
        endusers = endusers.filter(
            dancing_level__id=dancing_level_id
        )

    if dancing_style_id != "!":
        endusers = endusers.filter(
            favourite_dancing_style__id=dancing_style_id
        )

    endusers = endusers.order_by(order_by_field)

    return render(
        request,
        "app/users.html",
        {
            "selected_dancing_level_id": dancing_level_id,
            "selected_dancing_style_id": dancing_style_id,
            "selected_order_criteria": order_criteria,
            "inverted_order_criteria": "+" if order_criteria == "-" else "-",
            "selected_order_key": order_key,
            "selected_search": search,
            "endusers": endusers
        }
    )


@login_required
def profile(request, username):
    try:
        enduser = EndUser.objects.get(user__username=username)
    except EndUser.DoesNotExist:
        messages.add_message(
            request,
            messages.ERROR,
            "El perfil de usuario al que está intentando acceder no existe."
        )
        return render(
            request,
            "app/message.html",
            {"url_next": reverse("users")}
        )

    liked_videos = enduser.video_set.all().order_by("title")
    if liked_videos:
        request.session["filtered_video_ids"] = [v.id for v in liked_videos]
    return render(
        request,
        "app/profile.html",
        {
            "enduser": enduser,
            "joined_days": enduser.joined_days(),
            "age": enduser.age(),
            "twitter_url": enduser.get_social_network_url("twitter"),
            "facebook_url": enduser.get_social_network_url("facebook"),
            "snapchat_url": enduser.get_social_network_url("snapchat"),
            "instagram_url": enduser.get_social_network_url("instagram"),
            "liked_videos": liked_videos
        }
    )
