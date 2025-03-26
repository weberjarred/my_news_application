"""
This file is used to register the models with the Django admin site.
A custom admin is created for the CustomUser model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Publisher, Article, Newsletter, Category


class CustomUserAdmin(UserAdmin):
    """
    CustomUserAdmin is a custom admin class for managing CustomUser model
    in the Django admin interface.

    Attributes:
        model (CustomUser): The model that this admin class is associated with.
        list_display (list): A list of field names to display
        in the admin list view.
    """
    model = CustomUser
    list_display = ["username", "email", "role", "is_staff"]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Publisher)
admin.site.register(Article)
admin.site.register(Newsletter)
admin.site.register(Category)
