"""
This file is used to creates serializers which converts Django model
instances into JSON files for API interaction.
"""

from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    ArticleSerializer is a ModelSerializer for the Article model.

    This serializer includes the following fields:
    - id: The unique identifier for the article (read-only).
    - title: The title of the article.
    - content: The content of the article.
    - publisher: The publisher of the article.
    - status: The publication status of the article.
    - is_deleted: A boolean indicating if the article is deleted.
    - created_at: The timestamp when the article was created (read-only).
    - updated_at: The timestamp when the article was last updated (read-only).

    Meta:
        model: The model that is being serialized.
        fields: The fields that are included in the serialization.
        read_only_fields: The fields that are read-only.
    """
    class Meta:
        """
        Meta class for the Article serializer.

        Attributes:
            model (Model): The model that is being serialized.
            fields (list): List of fields to be included in the serialization.
            read_only_fields (list): List of fields that are read-only
            and cannot be modified.
        """
        model = Article
        fields = [
            "id",
            "title",
            "content",
            "publisher",
            "status",
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]
