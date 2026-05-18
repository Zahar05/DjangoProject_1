from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_image, name='upload_image'),
    path('images/', views.image_list, name='image_list'),
    path('image/<int:image_id>/', views.image_detail, name='image_detail'),
    path('image/<int:image_id>/delete/', views.delete_image, name='delete_image'),
    path('image/<int:image_id>/download/', views.download_image, name='download_image'
         ),
]