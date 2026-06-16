from django.urls import path
from rest_framework.routers import DefaultRouter

from imageservice.views import (
    home,
    download_image,
    upload_image,
    image_list,
    image_detail,
    delete_image,
    ImageViewSet,
    gallery,
    recognize_image,
    RegisterView,
    login_view,
    logout_view,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


router = DefaultRouter()
router.register("api/images", ImageViewSet)

urlpatterns = [
    path('', home, name='home'),
     path(
         "api/register/", RegisterView.as_view(),
         name="register",
    ),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path('upload/', upload_image, name='upload_image'),
    path('images/', image_list, name='image_list'),
    path('image/<int:image_id>/', image_detail, name='image_detail'),
    path("image/<int:image_id>/recognize/", recognize_image, name="recognize_image"),
    path('image/<int:image_id>/delete/', delete_image, name='delete_image'),
    path('image/<int:image_id>/download/', download_image, name='download_image'),
    path("gallery/", gallery, name="gallery"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

urlpatterns += router.urls
