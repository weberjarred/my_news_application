"""
This file contains Contains forms for user
registration and article submission. The custom registration
form enforces password complexity (including uppercase,
lowercase, digit, and special character rules).
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Article, Category, Newsletter
import re


class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating a new user with additional fields and
    password validation.
    This form extends the default UserCreationForm to include additional fields
    and custom password validation logic.

    Attributes:
        Meta (class): Meta options for the form, specifying the model and
        fields to include.
        clean (method): Custom clean method to validate the passwords and
                        ensure they meet complexity requirements.

    Methods:
        clean: Validates that both passwords match and meet complexity
        requirements.

    Raises:
        forms.ValidationError: If the passwords do not match or do not meet
        complexity requirements.
    """
    class Meta:
        model = CustomUser
        fields = ("username", "email", "role")

    def clean(self):
        """
        Clean and validate the form data.
        This method checks that both password fields are provided and match.
        It also ensures that the password meets the complexity requirements:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character

        Raises:
            forms.ValidationError: If the passwords do not match or do not meet
            the complexity requirements.

        Returns:
            dict: The cleaned data.
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        # Check that both passwords were provided
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Passwords do not match.")

            # Validate password complexity on password2
            # (or password1, as they are the same)
            if not re.search(r"[A-Z]", password2):
                raise forms.ValidationError(
                    "Password must contain at least one uppercase letter."
                )
            if not re.search(r"[a-z]", password2):
                raise forms.ValidationError(
                    "Password must contain at least one lowercase letter."
                )
            if not re.search(r"\d", password2):
                raise forms.ValidationError(
                    "Password must contain at least one digit."
                )
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password2):
                raise forms.ValidationError(
                    "Password must contain at least one special character."
                )
        return cleaned_data


class LoginForm(AuthenticationForm):
    """
    LoginForm class that inherits from AuthenticationForm.

    This form is used for user authentication in the Django application.
    It does not add any additional fields or methods to the base
    AuthenticationForm.
    """
    pass


# Removed duplicate ArticleForm definition


class ArticleForm(forms.ModelForm):
    """
    ArticleForm is a Django ModelForm for creating and updating Article
    instances.

    Fields:
        title (CharField): The title of the article.
        content (TextField): The main content of the article.
        publisher (ForeignKey): The publisher of the article.
        category (ModelChoiceField): An optional field to select the category
                                     of the article from existing categories.
                                     Displays "Select a category" as the
                                     default empty label.

    Meta:
        model (Article): The model that this form is associated with.
        fields (list): The list of fields to include in the form.
    """
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,  # Set to True if you want to enforce selection
        empty_label="Select a category",
    )

    class Meta:
        model = Article
        fields = ["title", "content", "publisher", "category"]


class NewsletterForm(forms.ModelForm):
    """
    A form for creating and updating Newsletter instances.

    This form is based on the Newsletter model and includes the following
    fields:
    - title: The title of the newsletter.
    - content: The content of the newsletter.
    - publisher: The publisher of the newsletter.

    Note: The 'approved' field is not included by default. If you want editors
    to toggle it, you can add 'approved' to the fields list.
    """
    class Meta:
        model = Newsletter
        fields = ["title", "content", "publisher"]
        # (Add 'approved' if you want editors to toggle it, or keep it out)
