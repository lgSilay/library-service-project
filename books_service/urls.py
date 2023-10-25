from rest_framework.routers import DefaultRouter

from .views import BookViewSet, AuthorViewSet


router = DefaultRouter()
router.register("books", BookViewSet, basename="books")
router.register("authors", AuthorViewSet, basename="authors")

urlpatterns = router.urls


app_name = "books_service"
