import logging

from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import ImageForm
from .models import Image

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

    return response


def home(request):
    logger.info("Home page opened")
    return render(request, "imageservice/home.html")


def upload_image(request):
    if request.method == "POST":
        logger.info("Upload request received")

        form = ImageForm(request.POST, request.FILES)

        if form.is_valid():
            image = form.save()

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
        image.delete()        # удалить запись из БД

        logger.info("Image deleted successfully id=%s", image_id)

        return redirect("image_list")

    logger.info("Delete confirmation page opened for image id=%s", image_id)

    return render(request, "imageservice/delete.html", {"image": image})

# Create your views here.
