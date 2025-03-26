"""
This file utilizes Django signals to automatically send an email to
subscribers and post the article to X when an article is approved.

The signal is triggered on post-save of an Article.

When an editor approves an article in the approval view,
the post_save signal in signals.py automatically triggers email
notifications to subscribers and publishes the article on X
using the tweet.py function.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Article
from django.core.mail import send_mail
from django.conf import settings
from .functions.tweet import post_tweet


@receiver(pre_save, sender=Article)
def store_old_status(sender, instance, **kwargs):
    """
    Signal handler to store the old status of an Article instance before it
    is saved.

    This function is intended to be connected to the pre-save signal of the
    Article model.
    It checks if the instance has a primary key (pk), indicating that it is
    an existing record.
    If so, it retrieves the current status of the article from the database
    and stores it in the instance's _old_status attribute. If the instance
    does not have a
    primary key, it sets
    the _old_status attribute to None.

    Args:
        sender (Model): The model class that sent the signal.
        instance (Article): The instance of the Article model that is
        being saved.
        **kwargs: Additional keyword arguments.
    """
    if instance.pk:
        old_article = Article.objects.filter(pk=instance.pk).first()
        instance._old_status = old_article.status if old_article else None
    else:
        instance._old_status = None


@receiver(post_save, sender=Article)
def article_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for the post-save signal of the Article model.
    This function is triggered after an Article instance is saved. It compares
    the old status of the article to the new one. If the status has changed
    from 'pending' to 'approved', it performs the following actions:
    1. Notifies subscribers via email about the newly approved article.
    2. Posts a tweet about the new article on X (formerly Twitter).

    Args:
        sender (type): The model class that sent the signal.
        instance (Article): The instance of the Article that was saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.

    After saving the Article, compare the old status to the new one.
    If it changed from 'pending' to 'approved', notify subscribers
    and post to X (formerly Twitter).
    """
    # Retrieve the old status that was set in pre_save
    old_status = getattr(instance, "_old_status", None)
    new_status = instance.status

    # If the status changed from 'pending' to 'approved'
    if old_status == "pending" and new_status == "approved":
        # 1. Notify subscribers by email
        subscribers_emails = set()
        if instance.publisher:
            for reader in instance.publisher.subscribed_readers.all():
                subscribers_emails.add(reader.email)
        for reader in instance.author.subscribed_readers_by.all():
            subscribers_emails.add(reader.email)

        if subscribers_emails:
            send_mail(
                subject=f"New Article Published: {instance.title}",
                message=(
                    f"Hello,\n\n"
                    f"A new article titled '{instance.title}' by "
                    f"{instance.author.username} "
                    f"has just been approved.\n\n"
                    f"Content Preview:\n{instance.content[:200]}..."
                ),
                from_email=getattr(
                    settings, "DEFAULT_FROM_EMAIL", "noreply@example.com"
                ),
                recipient_list=list(subscribers_emails),
                fail_silently=True,
            )

        # 2. Post to X (formerly Twitter)
        post_tweet(instance)
