import shutil
import tempfile
from io import BytesIO

from PIL import Image as PILImage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import HttpResponse
from django.test import TestCase, override_settings, RequestFactory
from django.urls import reverse

from .models import Image
from .middleware import RequestLoggingMiddleware

from django.contrib.auth.models import AnonymousUser

TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ImageViewsTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def create_test_image(self):
        """
        Создает валидное JPEG-изображение в памяти.
        Это необходимо для корректной проверки ImageField.
        """
        file = BytesIO()

        image = PILImage.new("RGB", (100, 100), color="red")
        image.save(file, "JPEG")
        file.seek(0)

        return SimpleUploadedFile(
            "test.jpg",
            file.read(),
            content_type="image/jpeg",
        )

    def create_image_object(self):
        """
        Создает объект Image с валидным файлом изображения.
        """
        return Image.objects.create(
            title="Test image",
            image=self.create_test_image(),
        )

    def test_home_page(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_upload_page_get(self):
        response = self.client.get(reverse("upload_image"))
        self.assertEqual(response.status_code, 200)

    def test_upload_image_post(self):
        response = self.client.post(
            reverse("upload_image"),
            {
                "title": "Uploaded image",
                "image": self.create_test_image(),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Image.objects.count(), 1)

    def test_image_list(self):
        self.create_image_object()

        response = self.client.get(reverse("image_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test image")

    def test_image_detail(self):
        image = self.create_image_object()

        response = self.client.get(
            reverse("image_detail", args=[image.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test image")

    def test_download_image(self):
        image = self.create_image_object()

        response = self.client.get(
            reverse("download_image", args=[image.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("attachment", response["Content-Disposition"])

    def test_delete_image_get(self):
        image = self.create_image_object()

        response = self.client.get(
            reverse("delete_image", args=[image.id])
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_image_post(self):
        image = self.create_image_object()

        response = self.client.post(
            reverse("delete_image", args=[image.id])
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Image.objects.count(), 0)


class RequestLoggingMiddlewareTests(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_get_client_ip_remote_addr(self):
        request = self.factory.get("/")
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        middleware = RequestLoggingMiddleware(
            lambda request: HttpResponse()
        )

        ip = middleware.get_client_ip(request)

        self.assertEqual(ip, "127.0.0.1")

    def test_get_client_ip_forwarded_for(self):
        request = self.factory.get("/")

        request.META["HTTP_X_FORWARDED_FOR"] = (
            "10.0.0.1, 172.16.0.1"
        )

        middleware = RequestLoggingMiddleware(
            lambda request: HttpResponse()
        )

        ip = middleware.get_client_ip(request)

        self.assertEqual(ip, "10.0.0.1")

    def test_middleware_returns_response(self):
        request = self.factory.get("/test/")
        request.user = AnonymousUser()

        middleware = RequestLoggingMiddleware(
            lambda request: HttpResponse("OK")
        )

        response = middleware(request)

        self.assertEqual(response.status_code, 200)