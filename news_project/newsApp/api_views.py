"""
Defines RESTful API views using Django REST Framework.
For example, the ArticleListAPI view returns articles filtered by
the reader’s subscriptions if the logged-in user is a reader.
"""

from rest_framework import generics, permissions
from .models import Article
from .serializers import ArticleSerializer
from django.db import models


class ArticleListCreateAPI(generics.ListCreateAPIView):
    """
    API view for listing and creating articles.
    This view supports the following operations:
    - GET: List all approved articles. If the user is a reader, only
      articles from subscribed publishers and journalists are listed.
    - POST: Create a new article with the current user set as the author.

    Attributes:
        queryset (QuerySet): The base queryset for retrieving articles.
        serializer_class (Serializer): The serializer class used for
        article data.
        permission_classes (list): The list of permission classes that
        determine access to this view.

    Methods:
        get_queryset(self):
            Returns a queryset of approved articles. If the user is a reader,
            filters the articles to only include those from subscribed
            publishers and journalists.
        perform_create(self, serializer):
            Saves the new article with the current user set as the author.
    """
    queryset = Article.objects.all()  # or filter by role if needed
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns a queryset of approved articles based on the user's role
        and subscriptions.

        If the user is a reader, the queryset will include articles from
        publishers and journalists the user is subscribed to. Otherwise,
        it will return all approved articles.

        Returns:
            QuerySet: A queryset of approved articles filtered by the user's
            subscriptions if applicable.
        """
        user = self.request.user
        if user.role == "reader":
            publisher_ids = user.subscriptions_publishers.values_list(
                "id", flat=True
            )
            journalist_ids = user.subscriptions_journalists.values_list(
                "id", flat=True
            )
            return (
                Article.objects.filter(status="approved")
                .filter(
                    models.Q(publisher__id__in=publisher_ids)
                    | models.Q(author__id__in=journalist_ids)
                )
                .distinct()
            )
        return Article.objects.filter(status="approved")

    def perform_create(self, serializer):
        """
        Saves the serializer instance with the author set to the current user.

        Args:
            serializer (Serializer): The serializer instance to be saved.
        """
        # Automatically set the author to the current user
        serializer.save(author=self.request.user)
