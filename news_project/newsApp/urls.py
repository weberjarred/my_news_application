"""
This file contains the URL patterns defined for the web views.
"""

from django.urls import path
from . import views
from .views import (
    PendingNewslettersListView,
    approve_newsletter,
    reject_newsletter,
)


urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("", views.homepage, name="homepage"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("article/create/", views.article_create, name="article_create"),
    path("article/<int:pk>/", views.article_detail, name="article_detail"),
    path("article/approval/", views.article_approval, name="article_approval"),
    path(
        "article/<int:pk>/delete/",
        views.article_delete,
        name="article_delete"
    ),
    # edit URL
    path("article/<int:pk>/edit/", views.article_edit, name="article_edit"),
    path(
        "subscribe/<int:journalist_id>/",
        views.subscribe_journalist,
        name="subscribe_journalist",
    ),
    path("subscriptions/", views.subscriptions, name="subscriptions"),
    path(
        "journalist/<int:journalist_id>/",
        views.journalist_articles,
        name="journalist_articles",
    ),
    path(
        "subscribe/<int:journalist_id>/",
        views.subscribe_journalist,
        name="subscribe_journalist",
    ),
    path(
        "article/<int:pk>/delete/", views.article_delete, name="article_delete"
    ),  # for editors
    path(
        "article/<int:pk>/delete_by_author/",
        views.article_delete_by_author,
        name="article_delete_by_author",
    ),
    path(
        "category/<slug:slug>/",
        views.category_articles,
        name="category_articles"
    ),
    path("newsletters/", views.newsletter_list, name="newsletter_list"),
    path(
        "newsletters/<int:pk>/",
        views.newsletter_detail,
        name="newsletter_detail"
    ),
    path(
        "newsletters/create/",
        views.newsletter_create,
        name="newsletter_create"
    ),
    path(
        "newsletters/<int:pk>/edit/",
        views.newsletter_edit,
        name="newsletter_edit"
    ),
    path(
        "newsletters/<int:pk>/delete/",
        views.newsletter_delete,
        name="newsletter_delete",
    ),
    path(
        "newsletters/pending/",
        PendingNewslettersListView.as_view(),
        name="pending_newsletters",
    ),
    path(
        "newsletters/<int:pk>/approve/",
        approve_newsletter,
        name="approve_newsletter"
    ),
    path(
        "newsletters/<int:pk>/reject/",
        reject_newsletter,
        name="reject_newsletter",
    ),
]
