from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse
from .models import Image
from .forms import ImageForm


def download_image(request, image_id):
    image_obj = get_object_or_404(Image, id=image_id)

    response = FileResponse(image_obj.image.open(), as_attachment=True)
    response["Content-Disposition"] = f'attachment; filename="{image_obj.image.name.split("/")[-1]}"'

    return response


def home(request):
    return render(request, 'imageservice/home.html')


def upload_image(request):
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('image_list')
    else:
        form = ImageForm()

    return render(request, 'imageservice/upload.html', {'form': form})


def image_list(request):
    images = Image.objects.all().order_by('-uploaded_at')
    return render(request, 'imageservice/list.html', {'images': images})


def image_detail(request, image_id):
    image = get_object_or_404(Image, id=image_id)
    return render(request, 'imageservice/detail.html', {'image': image})


def delete_image(request, image_id):
    image = get_object_or_404(Image, id=image_id)

    if request.method == 'POST':
        image.image.delete()  # удалить файл с диска
        image.delete()        # удалить запись из БД
        return redirect('image_list')

    return render(request, 'imageservice/delete.html', {'image': image})

# Create your views here.
