import logging
import requests

from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ImageForm
from .models import Image

from rest_framework.viewsets import ModelViewSet

from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ImageSerializer,
    UserRegistrationSerializer,
)

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


from .metrics import (
    IMAGES_UPLOADED,
    IMAGES_DOWNLOADED,
    IMAGES_DELETED,
    USERS_REGISTERED,
)


logger = logging.getLogger(__name__)


def download_image(request, image_id):
    image_obj = get_object_or_404(Image, id=image_id)

    logger.info(
        "Downloading image id=%s filename=%s",
        image_obj.id,
        image_obj.image.name,
    )

    response = FileResponse(image_obj.image.open(), as_attachment=True)
    response["Content-Disposition"] = (
        f'attachment; filename="{image_obj.image.name.split("/")[-1]}"'
    )

    IMAGES_DOWNLOADED.inc()

    return response


def home(request):
    message = ""

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "register":
            username = request.POST.get("username")
            password = request.POST.get("password")

            if User.objects.filter(username=username).exists():
                message = "User already exists"
            else:
                User.objects.create_user(
                    username=username,
                    password=password
                )

                USERS_REGISTERED.inc()
                message = "User created successfully"

        elif action == "login":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user:
                login(request, user)
                message = "Logged in successfully"
            else:
                message = "Invalid credentials"

        elif action == "logout":
            logout(request)
            message = "Logged out"

    return render(request, "imageservice/home.html", {
        "message": message,
        "user": request.user
    })


def upload_image(request):
    if request.method == "POST":
        logger.info("Upload request received")

        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()

            IMAGES_UPLOADED.inc()

            logger.info(
                "Image uploaded successfully id=%s filename=%s",
                image.id,
                image.image.name,
            )

            return redirect("image_list")

        logger.warning("Invalid upload form: %s", form.errors)

    else:
        form = ImageForm()

    return render(request, "imageservice/upload.html", {"form": form})


def image_list(request):
    images = Image.objects.all().order_by("-uploaded_at")

    logger.info("Image list viewed. Count=%s", images.count())

    return render(request, "imageservice/list.html", {"images": images})


def image_detail(request, image_id):
    image = get_object_or_404(Image, id=image_id)

    logger.info(
        "Image detail viewed id=%s filename=%s",
        image.id,
        image.image.name,
    )

    return render(request, "imageservice/detail.html", {"image": image})


def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)

    if request.method == "POST":
        logger.info(
            "Deleting image id=%s filename=%s",
            image.id,
            image.image.name,
        )

        image.image.delete()  # удалить файл с диска

        IMAGES_DELETED.inc()

        image.delete()        # удалить запись из БД

        logger.info("Image deleted successfully id=%s", image_id)

        return redirect("image_list")

    logger.info("Delete confirmation page opened for image id=%s", image_id)

    return render(request, "imageservice/delete.html", {"image": image})


class ImageViewSet(ModelViewSet):
    queryset = Image.objects.all().order_by("-uploaded_at")
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


def gallery(request):
    images = Image.objects.all().order_by("-uploaded_at")

    return render(
        request,
        "imageservice/gallery.html",
        {"images": images}
    )

class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()

            USERS_REGISTERED.inc()

            # 🔥 создаём JWT сразу после регистрации
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User created successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        return render(request, "imageservice/home.html", {
            "error": "Invalid credentials"
        })

    return redirect("home")

def logout_view(request):
    logout(request)
    return redirect("home")

def recognize_image(request, image_id):

    response = requests.post(
        "http://127.0.0.1:8001/analyze_doc",
        json={
            "image_id": image_id,
            "email": "zaipulla1989@gmail.com",
        },
        timeout=10,
    )

    logger.info(
        "Recognition started for image_id=%s. Response=%s",
        image_id,
        response.text,
    )

    return redirect("image_list")
