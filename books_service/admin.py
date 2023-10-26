from django.contrib import admin

from books_service.models import Author, Book


admin.site.register(Book)
admin.site.register(Author)
