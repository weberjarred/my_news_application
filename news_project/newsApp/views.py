"""
Views for the News Application.

This module defines view functions and class-based views for user
registration, authentication, article management (creation, editing,
deletion, listing, and detail), newsletter management, and subscription
functionality within the news application.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, ArticleForm, NewsletterForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Article, CustomUser, Category, Newsletter
from django.views.generic import ListView

# from django.core.mail import send_mail
# from django.conf import settings
from django.http import HttpResponseForbidden


def register(request):
    """
    Register a new user.

    Processes the registration form on POST requests. If the form is
    valid, a new user is created, a success message is displayed,
    the user is logged in, and they are redirected to the dashboard.
    For GET requests, an empty registration form is rendered.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered registration page or a redirect to the dashboard.

    :rtype: HttpResponse
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Registration successful.")
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, "newsApp/register.html", {"form": form})


def user_login(request):
    """
    Log in an existing user.

    Processes the authentication form on POST requests. If the form is valid,
    the user is logged in and redirected to the dashboard. For GET requests, an
    empty authentication form is rendered.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered login page or a redirect to the dashboard.

    :rtype: HttpResponse
    """
    from django.contrib.auth.forms import AuthenticationForm

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "newsApp/login.html", {"form": form})


def user_logout(request):
    """
    Log out the current user.

    Logs out the user and redirects them to the login page.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A redirect to the login page.

    :rtype: HttpResponse
    """
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    """
    Display the dashboard for the logged-in user.

    For journalists, displays all authored articles.
    For editors, displays pending articles. The context is built based
    on the user's role and then rendered in the dashboard template.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered dashboard page.

    :rtype: HttpResponse
    """
    context = {}
    if request.user.role == "journalist":
        # Show all articles authored by the journalist
        user_articles = Article.objects.filter(
            author=request.user, is_deleted=False
        ).order_by("-created_at")
        context["user_articles"] = user_articles

    elif request.user.role == "editor":
        # Show only articles that are pending
        pending_articles = Article.objects.filter(
            status="pending", is_deleted=False
        ).order_by("-created_at")
        context["pending_articles"] = pending_articles

    return render(request, "newsApp/dashboard.html", context)


@login_required
def article_create(request):
    """
    Create a new article.

    Only users with the role 'journalist' can create articles.
    On POST, the submitted ArticleForm is validated and saved with
    the current user as the author. On GET,
    an empty ArticleForm is rendered.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered article creation form or a redirect to the dashboard.

    :rtype: HttpResponse
    """
    # Only journalists are allowed to create articles.
    if request.user.role != "journalist":
        messages.error(request, "Only journalists can create articles.")
        return redirect("dashboard")
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, "Article submitted for approval.")
            return redirect("dashboard")
        else:
            # Log or print form errors for debugging
            print(form.errors)
            messages.error(request, "There were errors in your submission.")
    else:
        form = ArticleForm()
    return render(request, "newsApp/article_form.html", {"form": form})


@login_required
@user_passes_test(lambda u: u.role == "editor")
def article_approval(request):
    """
    Approve or reject pending articles.

    For POST requests, retrieves the article by its ID and processes
    the approval or rejection based on the submitted action. Updates
    the article status accordingly and redirects to the dashboard.
    For GET requests, renders the article approval template.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered approval page or a redirect to the dashboard.

    :rtype: HttpResponse
    """
    pending_articles = Article.objects.filter(
        status="pending", is_deleted=False
    )

    if request.method == "POST":
        article_id = request.POST.get("article_id")
        action = request.POST.get("action")  # "approve" or "reject"
        article = get_object_or_404(
            Article, id=article_id, status="pending", is_deleted=False
        )

        if action == "approve":
            article.approve(request.user)  # sets status='approved'
            messages.success(request, "Article approved.")
            # Signals can handle notifications to subscribers.

        elif action == "reject":
            article.reject()  # sets status='rejected'
            messages.warning(request, "Article rejected.")
            # Optionally email the author about rejection.

        return redirect("dashboard")  # or redirect('article_approval')

    return render(
        request,
        "newsApp/article_approval.html",
        {"pending_articles": pending_articles}
    )


def article_list(request):
    """
    List all approved articles.

    Retrieves articles with status 'approved' that are not deleted
    and orders them by creation date in descending order. Renders
    the article list template.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered article list page.

    :rtype: HttpResponse
    """
    articles = Article.objects.filter(
        status="approved", is_deleted=False
    ).order_by("-created_at")
    return render(request, "newsApp/article_list.html", {"articles": articles})


@login_required
def article_detail(request, pk):
    """
    Display the details of a specific article.

    Editors can view any non-deleted article. Journalists can view
    their own articles regardless of status, but cannot view others'
    unapproved articles. Readers see only approved articles.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the article.
    :type pk: int

    :return: A rendered article detail page or an HTTP forbidden response.

    :rtype: HttpResponse
    """
    if request.user.role == "editor":
        # Editors can view any article that isn’t soft-deleted.
        article = get_object_or_404(Article, pk=pk, is_deleted=False)
    elif request.user.role == "journalist":
        # Journalists can view their own articles regardless of status.
        article = get_object_or_404(Article, pk=pk, is_deleted=False)
        if article.author != request.user and article.status != "approved":
            # Prevent journalists from viewing others' unapproved articles.
            return HttpResponseForbidden(
                "You are not allowed to view this article."
            )
    else:
        # Readers see only approved articles.
        article = get_object_or_404(
            Article, pk=pk, status="approved", is_deleted=False
        )

    return render(request, "newsApp/article_detail.html", {"article": article})


@login_required
def article_delete(request, pk):
    """
    Soft-delete an article.

    Editors may delete any article, while journalists can only delete
    their own articles if the article status is 'rejected'. On a POST
    request, marks the article as deleted and redirects to the
    dashboard; on a GET request, renders a delete confirmation
    template.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the article.
    :type pk: int

    :return: A rendered confirmation page or a redirect.

    :rtype: HttpResponse
    """
    article = get_object_or_404(Article, pk=pk, is_deleted=False)

    # Access checks:
    if request.user.role == "editor":
        # Editor can delete if needed
        pass
    elif request.user.role == "journalist":
        # Journalist can only delete if it’s their own & e.g. status='rejected'
        if article.author != request.user or article.status != "rejected":
            messages.error(
                request, "You do not have permission to delete this article."
            )
            return redirect("article_detail", pk=pk)
    else:
        messages.error(
            request, "You do not have permission to delete this article."
        )
        return redirect("article_detail", pk=pk)

    if request.method == "POST":
        # Actually soft-delete
        article.is_deleted = True
        article.save()
        messages.success(request, "Article has been removed.")
        # Could redirect to dashboard or article_list
        return redirect("dashboard")

    # GET → show a custom confirmation template
    return render(
        request,
        "newsApp/article_confirm_delete.html",
        {"article": article}
    )


# Create the Subscription View
@login_required
def subscribe_journalist(request, journalist_id):
    """
    Subscribe the current reader to a journalist.

    Only readers can subscribe. Adds the journalist to the reader's
    subscriptions and redirects to the subscriptions page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param journalist_id: The primary key of the journalist.
    :type journalist_id: int

    :return: A redirect to the subscriptions page.

    :rtype: HttpResponse
    """
    if request.user.role != "reader":
        messages.error(request, "Only readers can subscribe to journalists.")
        return redirect("dashboard")

    journalist = get_object_or_404(
        CustomUser, pk=journalist_id, role="journalist"
    )
    request.user.subscriptions_journalists.add(journalist)
    messages.success(request, f"You have subscribed to {journalist.username}.")
    return redirect("subscriptions")  # or anywhere you prefer


# Create a “Subscriptions” Page
@login_required
def subscriptions(request):
    """
    Display the subscriptions page for readers.

    Retrieves all subscribed journalists for the reader and renders the
    subscriptions template.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered subscriptions page.

    :rtype: HttpResponse
    """
    # Ensure only readers see subscriptions
    if request.user.role != "reader":
        messages.error(request, "Only readers have subscriptions.")
        return redirect("dashboard")

    # Retrieve all journalists the reader is subscribed to
    subscribed_journalists = request.user.subscriptions_journalists.all()
    return render(
        request,
        "newsApp/subscriptions.html",
        {"subscribed_journalists": subscribed_journalists},
    )


@login_required
def journalist_articles(request, journalist_id):
    """
    Display all approved articles for a given journalist.

    Retrieves the journalist by ID and fetches their approved,
    non-deleted articles, then renders the journalist articles
    template.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param journalist_id: The primary key of the journalist.
    :type journalist_id: int

    :return: A rendered page with the journalist's articles.

    :rtype: HttpResponse
    """
    # Get the journalist by id and ensure their role is 'journalist'
    journalist = get_object_or_404(
        CustomUser, id=journalist_id, role="journalist"
    )
    # Retrieve only approved, non-deleted articles by this journalist
    articles = Article.objects.filter(
        author=journalist, status="approved", is_deleted=False
    ).order_by("-created_at")

    return render(
        request,
        "newsApp/journalist_articles.html",
        {"journalist": journalist, "articles": articles},
    )


# separate view that allows a journalist to delete (soft-delete) an
# article if it’s rejected
@login_required
def article_delete_by_author(request, pk):
    """
    Allow a journalist to delete their own rejected article.

    Ensures the article is not already deleted, is authored by the
    current user, and has a status of 'rejected'. On POST, marks the
    article as deleted and redirects to the dashboard; on GET, renders
    a confirmation template.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the article.
    :type pk: int

    :return: A rendered confirmation page or a redirect.

    :rtype: HttpResponse
    """
    # Only allow deletion if the article is not already deleted,
    # is authored by the logged-in journalist, and is rejected.
    article = get_object_or_404(
        Article, pk=pk, is_deleted=False, author=request.user,
        status="rejected"
    )

    if request.method == "POST":
        article.is_deleted = True
        article.save()
        messages.success(request, "Article deleted successfully.")
        return redirect("dashboard")

    return render(
        request,
        "newsApp/article_confirm_delete.html",
        {"article": article}
    )


def category_articles(request, slug):
    """
    Display articles belonging to a specific category.

    Retrieves the category using the slug and filters for approved,
    non-deleted articles within that category, then renders the
    corresponding template.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param slug: The slug identifier for the category.
    :type slug: str

    :return: A rendered page with articles for the category.

    :rtype: HttpResponse
    """
    category = get_object_or_404(Category, slug=slug)
    # Filter articles that belong to this category (and perhaps are approved,
    # not deleted, etc.)
    articles = Article.objects.filter(
        category=category, status="approved", is_deleted=False
    )
    return render(
        request,
        "newsApp/category_articles.html",
        {
            "category": category,
            "articles": articles,
        },
    )


@login_required
def homepage(request):
    """
    Display the homepage with a list of approved articles.

    Retrieves all approved, non-deleted articles ordered by newest
    first and renders the homepage template.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered homepage.

    :rtype: HttpResponse
    """
    # Get all approved, non-deleted articles ordered by newest first
    articles = Article.objects.filter(
        status="approved", is_deleted=False
    ).order_by("-created_at")
    return render(request, "newsApp/homepage.html", {"articles": articles})


# Add a view to edit an article
@login_required
def article_edit(request, pk):
    """
    Edit an existing article.

    Allows editing only if the current user is an editor or the
    journalist who authored the article. Processes the article
    form on POST, saving updates if valid, and renders the edit
    form on GET.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the article.
    :type pk: int

    :return: A rendered edit page or a redirect after successful update.

    :rtype: HttpResponse
    """
    article = get_object_or_404(Article, pk=pk, is_deleted=False)

    # Allow only editor OR the journalist who authored the article.
    if request.user.role != "editor" and (
        request.user.role != "journalist" or article.author != request.user
    ):
        return HttpResponseForbidden(
            "You are not allowed to edit this article."
        )

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Article updated successfully.")
            return redirect("article_detail", pk=article.pk)
        else:
            messages.error(request, "There were errors in your submission.")
    else:
        form = ArticleForm(instance=article)

    return render(
        request,
        "newsApp/article_edit.html",
        {"form": form, "article": article}
    )


def newsletter_list(request):
    """
    List newsletters.

    Retrieves all newsletters (or a filtered set) and renders them in
    the newsletter list template.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered newsletter list page.

    :rtype: HttpResponse
    """
    # Fetch all newsletters or filter them as needed
    newsletters = Newsletter.objects.all()

    # Pass them into the template with a custom context key
    return render(
        request, "newsApp/newsletter_list.html", {"newsletters": newsletters}
    )


# display the details of a single newsletter
@login_required
def newsletter_detail(request, pk):
    """
    Display the details of a single newsletter.

    Retrieves a newsletter by its primary key and renders the
    newsletter detail template.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the newsletter.
    :type pk: int

    :return: A rendered newsletter detail page.

    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return render(
        request, "newsApp/newsletter_detail.html", {"newsletter": newsletter}
    )


@login_required
def newsletter_create(request):
    """
    Create a new newsletter.

    Only journalists are allowed to create newsletters. On POST,
    processes the newsletter form, assigns the current user as the
    author, and saves the newsletter. On GET, renders an empty
    newsletter form.

    :param request: The HTTP request object.
    :type request: HttpRequest

    :return: A rendered newsletter creation page or a redirect to the
    newsletter list.

    :rtype: HttpResponse
    """
    # Only journalists can create
    if request.user.role != "journalist":
        messages.error(request, "Only journalists can create newsletters.")
        return redirect("dashboard")

    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            newsletter = form.save(commit=False)
            newsletter.journalist = request.user  # set the author
            newsletter.save()
            messages.success(request, "Newsletter created successfully.")
            return redirect("newsletter_list")  # or wherever you want
    else:
        form = NewsletterForm()

    return render(request, "newsApp/newsletter_create.html", {"form": form})


@login_required
def newsletter_edit(request, pk):
    """
    Edit an existing newsletter.

    Checks user role and ownership before allowing editing. On POST,
    updates the newsletter if the form is valid; on GET, renders
    the edit form.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the newsletter.
    :type pk: int

    :return: A rendered newsletter edit page or a redirect after a
    successful update.

    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Check role & ownership
    if request.user.role == "editor":
        pass  # Editor can always edit
    elif request.user.role == "journalist":
        if newsletter.journalist != request.user:
            messages.error(
                request, "You cannot edit someone else’s newsletter."
            )
            return redirect("newsletter_detail", pk=pk)
    else:
        messages.error(
            request, "You do not have permission to edit this newsletter."
        )
        return redirect("newsletter_detail", pk=pk)

    if request.method == "POST":
        form = NewsletterForm(request.POST, instance=newsletter)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter updated successfully.")
            return redirect("newsletter_detail", pk=newsletter.pk)
    else:
        form = NewsletterForm(instance=newsletter)

    return render(
        request,
        "newsApp/newsletter_edit.html",
        {
            "form": form,
            "newsletter": newsletter,
        },
    )


# Either a journalist (who owns it) or an editor can delete. Readers cannot.
@login_required
def newsletter_delete(request, pk):
    """
    Delete a newsletter.

    Checks that the current user is either an editor or the author
    of the newsletter. On POST, deletes the newsletter and redirects
    to the newsletter list. On GET, renders a confirmation template.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the newsletter.
    :type pk: int

    :return: A rendered delete confirmation page or a redirect.

    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)

    # Check role & ownership
    if request.user.role == "editor":
        pass
    elif request.user.role == "journalist":
        if newsletter.journalist != request.user:
            messages.error(
                request, "You cannot delete someone else’s newsletter."
            )
            return redirect("newsletter_detail", pk=pk)
    else:
        messages.error(
            request, "You do not have permission to delete this newsletter."
        )
        return redirect("newsletter_detail", pk=pk)

    if request.method == "POST":
        newsletter.delete()  # or implement "soft-delete" if desired
        messages.success(request, "Newsletter deleted successfully.")
        return redirect("newsletter_list")

    return render(
        request,
        "newsApp/newsletter_confirm_delete.html",
        {
            "newsletter": newsletter,
        },
    )


#  Journalist Submits Newsletter for Approval
def submit_for_approval(request, pk):
    """
    Submit a newsletter for approval.

    Verifies that the current user is the author of the newsletter,
    changes its status to 'pending', saves it, and redirects to the
    newsletter detail page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the newsletter.
    :type pk: int

    :return: A redirect to the newsletter detail page.

    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if newsletter.author != request.user:
        return HttpResponseForbidden(
            "You are not the author of this newsletter."
        )

    newsletter.status = "pending"
    newsletter.save()
    return redirect("newsletter_detail", pk=newsletter.pk)


# An editor can see all newsletters with status='pending'.
# You can create a list view for that:
class PendingNewslettersListView(ListView):
    """
    ListView to display pending newsletters.

    Only newsletters with a status of 'pending' are shown. Access
    to this view is restricted to users in the 'Editors' group.
    """
    model = Newsletter
    template_name = "pending_newsletters.html"

    def get_queryset(self):
        """
        Retrieve newsletters that are pending approval.

        :return: A QuerySet of pending Newsletter objects.

        :rtype: QuerySet
        """
        # Only show newsletters that are pending
        return Newsletter.objects.filter(status="pending")

    def dispatch(self, request, *args, **kwargs):
        """
        Restrict view access to editors only.

        :param request: The HTTP request object.
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.

        :return: An HTTP response if permitted, otherwise an
        HttpResponseForbidden.

        :rtype: HttpResponse
        """
        # Restrict access to editors only
        if not request.user.groups.filter(name="Editors").exists():
            return HttpResponseForbidden("Only editors can see this page.")
        return super().dispatch(request, *args, **kwargs)


# Editor Approves a Newsletter
# simple function-based views for approving:
def approve_newsletter(request, pk):
    """
    Approve a newsletter.

    Checks if the current user is in the 'Editors' group, sets the
    newsletter's status to 'approved', and saves it. Redirects to
    the pending newsletters page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the newsletter.
    :type pk: int

    :return: A redirect to the pending newsletters page.

    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    # Check if user is an editor
    if not request.user.groups.filter(name="Editors").exists():
        return HttpResponseForbidden("Only editors can approve newsletters.")

    newsletter.status = "approved"
    newsletter.save()
    return redirect("pending_newsletters")  # or wherever you'd like


# Editor Rejects a Newsletter
# simple function-based views for rejecting:
def reject_newsletter(request, pk):
    """
    Reject a newsletter.

    Checks if the current user is in the 'Editors' group, sets the
    newsletter's status to 'rejected', and saves it. Redirects to
    the pending newsletters page.

    :param request: The HTTP request object.
    :type request: HttpRequest
    :param pk: The primary key of the newsletter.
    :type pk: int

    :return: A redirect to the pending newsletters page.

    :rtype: HttpResponse
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    # Check if user is an editor
    if not request.user.groups.filter(name="Editors").exists():
        return HttpResponseForbidden("Only editors can reject newsletters.")

    newsletter.status = "rejected"
    newsletter.save()
    return redirect("pending_newsletters")


class NewsletterListView(ListView):
    """
    ListView to display newsletters.

    For editors, journalists, or readers, all newsletters are
    shown; otherwise, only approved newsletters are displayed.
    """
    model = Newsletter
    template_name = "newsletter_list.html"

    def get_queryset(self):
        """
        Retrieve the queryset of newsletters based on the user's role.

        :return: A QuerySet of Newsletter objects.

        :rtype: QuerySet
        """
        # Show only approved newsletters to non-editors.
        # Editors might see all newsletters if you want that behavior.
        editors = self.request.user.groups.filter(name="Editors").exists()
        readers = self.request.user.groups.filter(name="Readers").exists()
        journalists = self.request.user.groups.filter(
            name="Journalists"
        ).exists()
        if editors or journalists or readers:
            return Newsletter.objects.all()
        else:
            return Newsletter.objects.filter(status="approved")
