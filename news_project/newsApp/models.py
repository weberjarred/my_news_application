"""
Defines the core data models for CustomUser, Publisher, Article,
and the Newsletter.

The CustomUser model extends Django’s AbstractUser and includes
a role field as well as subscriptions for readers.

The Article model has an “approved” flag, and the Publisher model
relates to multiple editors and journalists.

The custom user model and group assignments in models.py
guarantee user role assignments. The views limit access according
to these roles (for instance, only journalists are allowed to
create articles, while only editors can approve them).

Additionally, the registration form enforces password
complexity requirements.

This file includes a secure article removal feature for editors,
utilizing a soft-delete mechanism. Instead of permanently removing
an article from the database, you can simply mark it as removed
(or archived). This approach not only ensures an audit trail but
also allows for the recovery of the article if necessary.

"""

from django.db import models
from django.contrib.auth.models import AbstractUser


# Define available roles
ROLE_CHOICES = (
    ("reader", "Reader"),
    ("editor", "Editor"),
    ("journalist", "Journalist"),
)

STATUS_CHOICES = [
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("rejected", "Rejected"),
]


class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django AbstractUser model.
    Attributes:
        role (str): The role of the user, chosen from predefined ROLE_CHOICES.
        subscriptions_publishers (ManyToManyField): A many-to-many
        relationship to the Publisher model, representing the
        publishers the user is subscribed to.
        subscriptions_journalists (ManyToManyField): A many-to-many
        relationship to other CustomUser instances, representing the
        journalists the user is subscribed to.

    Methods:
        save(*args, **kwargs): Overrides the default save method to
        automatically add the user to a group based on their role.
        __str__(): Returns the username of the user.
    """
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    subscriptions_publishers = models.ManyToManyField(
        "Publisher", blank=True, related_name="subscribed_readers"
    )
    subscriptions_journalists = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="subscribed_readers_by"
    )

    def save(self, *args, **kwargs):
        """
        Overrides the save method to automatically add the user to a group
        based on their role.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Side Effects:
            Adds the user to a Django group corresponding to their role.
        """
        super().save(*args, **kwargs)
        # Automatically add user to a group based on their role.
        from django.contrib.auth.models import Group

        group, created = Group.objects.get_or_create(name=self.role)
        self.groups.add(group)

    def __str__(self):
        return self.username


class Publisher(models.Model):
    """
    Publisher model representing a publishing entity.

    Attributes:
        name (str): The name of the publisher.
        description (str): A brief description of the publisher.
        editors (ManyToManyField): A many-to-many relationship to CustomUser
        representing the editors associated with the publisher.
        journalists (ManyToManyField): A many-to-many relationship to
        CustomUser representing the journalists associated with the publisher.

    Methods:
        __str__(): Returns the string representation of the publisher,
        which is its name.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # A publisher can have multiple editors and journalists.
    editors = models.ManyToManyField(
        CustomUser, blank=True, related_name="editing_publishers"
    )
    journalists = models.ManyToManyField(
        CustomUser, blank=True, related_name="journalism_publishers"
    )

    def __str__(self):
        return self.name


# soft-delete functionality employed
# clearer distinction between “Pending,” “Approved,” and “Rejected,” added.
# A status field is added to the Article model.
class Article(models.Model):
    """
    Represents an article in the news application.

    Attributes:
        CATEGORY_CHOICES (list): List of category choices for the article.
        title (str): The title of the article.
        content (str): The content of the article.
        author (CustomUser): The author of the article.
        publisher (Publisher): The publisher of the article.
        category (Category): The category of the article.
        status (str): The status of the article, e.g., 'pending',
        'approved', 'rejected'.
        is_deleted (bool): Indicates if the article is deleted.
        created_at (datetime): The date and time when the article was created.
        updated_at (datetime): The date and time when the article was last
        updated.
        approved_by (CustomUser): The editor who approved the article.

    Methods:
        __str__(): Returns the title of the article.
        approve(editor): Sets the status to 'approved' and records
        the editor who approved it.
        reject(): Sets the status to 'rejected'.
        is_approved(): Checks if the article is in 'approved' status.
    """
    CATEGORY_CHOICES = [
        ("news", "News"),
        ("business", "Business"),
        ("tech", "Tech"),
        ("sport", "Sport"),
        ("investigations", "Investigations"),
        ("politics", "Politics"),
        ("opinion", "Opinion"),
        ("lifestyle", "Lifestyle"),
        ("food", "Food"),
        ("climate", "Climate / Weather"),
        ("projects", "Special Projects"),
    ]
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="articles"
    )
    publisher = models.ForeignKey(
        "Publisher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    category = models.ForeignKey(
        "Category",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    # Instead of just approved=True/False, we track multiple states:
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending"
    )

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_articles",
    )

    def __str__(self):
        return self.title

    # helper methods:
    def approve(self, editor):
        """Set status to 'approved' and record the editor who approved it."""
        self.status = "approved"
        self.approved_by = editor
        self.save()

    def reject(self):
        """Set status to 'rejected'."""
        self.status = "rejected"
        self.save()

    def is_approved(self):
        """Check if article is in 'approved' status."""
        return self.status == "approved"


# Create a Category Model
class Newsletter(models.Model):
    """
    Model representing a newsletter.

    Attributes:
        STATUS_CHOICES (list): List of tuples representing the possible
        status choices for a newsletter.
        title (CharField): The title of the newsletter.
        content (TextField): The content of the newsletter.
        journalist (ForeignKey): Foreign key to the CustomUser model,
        representing the journalist who wrote the newsletter.
        publisher (ForeignKey): Foreign key to the Publisher model,
        representing the publisher of the newsletter. Can be null or blank.
        status (CharField): The current status of the newsletter, with choices
        defined in STATUS_CHOICES. Defaults to "draft".
        created_at (DateTimeField): The date and time when the newsletter was
        created. Automatically set on creation.
        updated_at (DateTimeField): The date and time when the newsletter was
        last updated. Automatically set on update.

    Methods:
        __str__(): Returns the title of the newsletter as its string
        representation.
    """
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending Approval"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    journalist = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="newsletters"
    )
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="newsletters",
    )

    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft"
    )
    # approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Category(models.Model):
    """
    Category model representing a news category.
    Attributes:
        name (CharField): The name of the category, must be unique and have a
        maximum length of 100 characters.
        slug (SlugField): A unique slug for the category, used for URL
        generation.
    Methods:
        __str__(): Returns the string representation of the category,
        which is the category name.
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name
