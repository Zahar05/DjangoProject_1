from django.urls import path
from imageservice.views import home, download_image, upload_image, image_list, image_detail, delete_image
urlpatterns = [
    path('', home, name='home'),
    path('upload/', upload_image, name='upload_image'),
    path('images/', image_list, name='image_list'),
    path('image/<int:image_id>/', image_detail, name='image_detail'),
    path('image/<int:image_id>/delete/', delete_image, name='delete_image'),
    path('image/<int:image_id>/download/', download_image, name='download_image'
         ),
]