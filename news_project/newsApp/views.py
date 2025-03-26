"""
Contains the view functions for user registration, login,
logout, dashboard, article creation (for journalists), article
approval (for editors), article listing, and article detail pages.

Access control is enforced via decorators.
(Note: The email sending and posting to X are handled via Django signals.)

This section introduces a view enabling an editor to "remove"
an article. In this instance, the view shows a confirmation page
(through a GET request), and subsequently marks the article as deleted
when the editor confirms (using a POST request).

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
    Handle user registration.
    This view handles the registration of a new user. If the request
    method is POST, it processes the submitted registration form. If the
    form is valid, it saves the new user, displays a success message, logs
    the user in, and redirects to the dashboard. If the request method is
    not POST, it displays an empty registration form.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object with the rendered registration
        page or a redirect to the dashboard.
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
    Handle user login functionality.
    This view handles both GET and POST requests for user login. If the request
    method is POST, it processes the login form data, authenticates the user,
    and logs them in if the credentials are valid. If the request method is
    GET, it displays the login form.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object. If the login is successful, it
        redirects to the 'dashboard' page. Otherwise, it renders the login page
        with the login form.
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
    Logs out the current user and redirects them to the login page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponseRedirect: A redirect to the login page.
    """
    logout(request)
    return redirect("login")


@login_required
def dashboard(request):
    """
    Renders the dashboard view based on the user's role.

    Args:
        request (HttpRequest): The HTTP request object containing user
        information.

    Returns:
        HttpResponse: The rendered dashboard HTML page with context data.

    Context:
        user_articles (QuerySet): A queryset of articles authored by the
        journalist if the user is a journalist.
        pending_articles (QuerySet): A queryset of articles pending review
        if the user is an editor.
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
    Handle the creation of a new article by a journalist.

    This view function allows only users with the role of 'journalist' to
    create articles.
    If the user is not a journalist, they are redirected to the dashboard
    with an error message.
    If the request method is POST, it processes the submitted form data to
    create a new article.
    If the form is valid, the article is saved with the current user as the
    author, and a success message is displayed.
    If the form is invalid, the form errors are printed for debugging,
    and an error message is displayed.
    If the request method is not POST, an empty form is rendered.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object with the rendered template
        or a redirect.
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
    Handles the approval or rejection of pending articles.
    This view fetches all articles with a status of "pending" and
    displays them.
    If a POST request is made, it processes the approval or rejection
    of a specific article.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the article approval page with pending articles
        if GET request.
        HttpResponseRedirect: Redirects to the dashboard or article approval
        page after processing POST request.

    POST Parameters:
        article_id (str): The ID of the article to be approved or rejected.
        action (str): The action to be taken on the article,
                      either "approve" or "reject".

    Raises:
        Http404: If the article with the given ID does not exist
        or is not pending.
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
    View function to display a list of approved and non-deleted articles.

    This function retrieves articles from the database that have a status of
    "approved" and are not marked as deleted. The articles are then ordered
    by their creation date in descending order and rendered to the
    'newsApp/article_list.html' template.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML page displaying the list of articles.
    """
    articles = Article.objects.filter(
        status="approved", is_deleted=False
    ).order_by("-created_at")
    return render(request, "newsApp/article_list.html", {"articles": articles})


@login_required
def article_detail(request, pk):
    """
    View function to display the details of an article based on the user's
    role.

    Parameters:
    request (HttpRequest): The HTTP request object containing user
    information.
    pk (int): The primary key of the article to be retrieved.

    Returns:
    HttpResponse: The rendered article detail page or an HTTP 403
    Forbidden response.

    Behavior:
    - Editors can view any article that is not soft-deleted.
    - Journalists can view their own articles regardless of status.
    - They cannot view others' unapproved articles.
    - Readers can only view approved articles that are not soft-deleted.
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
    Handle the deletion of an article.
    This view function handles both GET and POST requests for
    deleting an article.
    It performs access checks based on the user's role and the article's
    status.

    Parameters:
    request (HttpRequest): The HTTP request object.
    pk (int): The primary key of the article to be deleted.

    Access Control:
    - Editors can delete any article.
    - Journalists can only delete their own articles if the article's status
      is 'rejected'.
    - Other users do not have permission to delete articles.

    Behavior:
    - If the request method is GET, renders a confirmation template.
    - If the request method is POST, performs a soft-delete by setting
      `is_deleted` to True and saves the article.

    Returns:
    HttpResponse: A response object that either renders a confirmation
    template or redirects to another view.
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
    Allows a reader to subscribe to a journalist.
    Args:
        request (HttpRequest): The HTTP request object containing user
        information.
        journalist_id (int): The ID of the journalist to subscribe to.

    Returns:
        HttpResponse: Redirects to the dashboard if the user is not a reader.
                      Redirects to the subscriptions page with a success
                      message if the subscription is successful.

    Raises:
        Http404: If the journalist with the given ID does not exist
        or is not a journalist.
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
    Handle the subscriptions view for readers.
    This view ensures that only users with the role of 'reader' can access
    their subscriptions.
    If the user is not a reader, an error message is displayed and the user
    is redirected to the dashboard.
    If the user is a reader, it retrieves all journalists the reader is
    subscribed to and renders the 'subscriptions.html' template with the
    list of subscribed journalists.

    Args:
        request (HttpRequest): The HTTP request object containing user
        information.

    Returns:
        HttpResponse: The rendered 'subscriptions.html' template with the
        context of subscribed journalists, or a redirect to the dashboard
        if the user is not a reader.
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
    View function to display articles written by a specific journalist.

    Args:
        request (HttpRequest): The HTTP request object.
        journalist_id (int): The ID of the journalist.

    Returns:
        HttpResponse: The rendered HTML page displaying the journalist's
        articles.

    Raises:
        Http404: If the journalist with the given ID does not exist
        or is not a journalist.

    The function performs the following actions:
        1. Retrieves the journalist by their ID and ensures their role is
           'journalist'.
        2. Retrieves only approved, non-deleted articles written by the
           journalist.
        3. Orders the articles by creation date in descending order.
        4. Renders the 'journalist_articles.html' template with the journalist
           and their articles.
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
    Handle the deletion of an article by its author.
    This view allows an author to delete their own article if it meets the
    following conditions:
    - The article is not already deleted.
    - The article is authored by the logged-in journalist.
    - The article has a status of "rejected".
    If the request method is POST, the article's `is_deleted` attribute is set
    to True, the article is saved, and a success message is displayed.
    The user is then redirected
    to the dashboard.
    If the request method is not POST, the article confirmation delete page
    is rendered.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the article to be deleted.

    Returns:
        HttpResponse: The response object containing the rendered template
        or a redirect.
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
    View function to display articles belonging to a specific category.

    Args:
        request (HttpRequest): The HTTP request object.
        slug (str): The slug of the category to filter articles by.

    Returns:
        HttpResponse: The rendered HTML page displaying the articles of the
        specified category.

    Raises:
        Http404: If the category with the given slug does not exist.
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
    View function for the homepage.

    This function retrieves all approved and non-deleted articles from the
    database, ordered by the newest first, and renders them on the homepage.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered homepage with the list of articles.
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
    Handle the editing of an article.
    This view allows only editors or the journalist who authored the article
    to edit it.
    If the user does not have the appropriate permissions,
    a 403 Forbidden response is returned.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the article to be edited.

    Returns:
        HttpResponse: The rendered HTML page for editing the article,
        or a redirect to the article detail page if the form is
        successfully submitted and valid. If the user does not have
        permission, an HttpResponseForbidden is returned.
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
    View function to display a list of newsletters.
    This function fetches all newsletters from the database and passes them
    to the 'newsletter_list.html' template for rendering.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered HTML page displaying the list of
        newsletters.
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
    View function to display the details of a specific newsletter.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the newsletter to be retrieved.

    Returns:
        HttpResponse: The rendered HTML page displaying the newsletter details.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return render(
        request, "newsApp/newsletter_detail.html", {"newsletter": newsletter}
    )


@login_required
def newsletter_create(request):
    """
    Handle the creation of a newsletter.
    Only users with the role of 'journalist' are allowed to create newsletters.
    If the user is not a journalist, an error message is displayed and the user
    is redirected to the dashboard.
    If the request method is POST, the function attempts to create a new
    newsletter using the data submitted in the form. If the form is valid, the
    newsletter is saved with the current user set as the journalist, a success
    message is displayed, and the user is redirected to the newsletter list.
    If the request method is not POST, an empty form is rendered.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The rendered newsletter creation page or a redirect
        response.
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
    View to edit an existing newsletter.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the newsletter to be edited.

    Returns:
        HttpResponse: The HTTP response object with the rendered template
        or a redirect.

    Raises:
        Http404: If the newsletter with the given primary key does not exist.

    Permissions:
        - Editors can always edit newsletters.
        - Journalists can only edit their own newsletters.
        - Other users do not have permission to edit newsletters.

    Template:
        newsApp/newsletter_edit.html

    Context:
        form (NewsletterForm): The form to edit the newsletter.
        newsletter (Newsletter): The newsletter instance being edited.
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
    Handle the deletion of a newsletter.
    This view function handles the deletion of a newsletter based on the user's
    role and ownership.
    Only users with the role of "editor" or the owner "journalist"
    of the newsletter can delete it.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the newsletter to be deleted.

    Returns:
        HttpResponse: Redirects to the newsletter detail page if the user
        does not have permission to delete the newsletter.
        HttpResponse: Redirects to the newsletter list page after
        successful deletion.
        HttpResponse: Renders the newsletter confirmation delete page
        if the request method is not POST.
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
    Handles the submission of a newsletter for approval.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the newsletter to be submitted for
        approval.

    Returns:
        HttpResponse: Redirects to the newsletter detail page if the
        submission is successful.
        HttpResponseForbidden: If the user is not the author of the newsletter.
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
    View to display a list of pending newsletters.
    This view inherits from Django's ListView and is used to display
    newsletters
    that have a status of "pending". It restricts access to users who are part
    of the "Editors" group.

    Attributes:
        model (Newsletter): The model that this view will operate on.
        template_name (str): The template to render the list of pending
        newsletters.

    Methods:
        get_queryset(): Returns a queryset of newsletters that are pending.
        dispatch(request, *args, **kwargs): Restricts access to the view to
        users
            who are part of the "Editors" group. Returns an HTTP 403 Forbidden
            response if the user is not an editor.
    """
    model = Newsletter
    template_name = "pending_newsletters.html"

    def get_queryset(self):
        """
        Returns a queryset of Newsletter objects that are pending.

        This method filters the Newsletter objects to include only those
        with a status of "pending".

        Returns:
            QuerySet: A queryset of pending Newsletter objects.
        """
        # Only show newsletters that are pending
        return Newsletter.objects.filter(status="pending")

    def dispatch(self, request, *args, **kwargs):
        """
        Overrides the dispatch method to restrict access to editors only.

        Args:
            request (HttpRequest): The HTTP request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            HttpResponseForbidden: If the user is not in the "Editors" group.
            HttpResponse: The response from the superclass dispatch method
            if the user is in the "Editors" group.
        """
        # Restrict access to editors only
        if not request.user.groups.filter(name="Editors").exists():
            return HttpResponseForbidden("Only editors can see this page.")
        return super().dispatch(request, *args, **kwargs)


# Editor Approves a Newsletter
# simple function-based views for approving:
def approve_newsletter(request, pk):
    """
    Approves a newsletter if the user is an editor.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the newsletter to be approved.

    Returns:
        HttpResponse: A redirect to the pending newsletters page if the
        newsletter is approved.
        HttpResponseForbidden: If the user is not an editor.

    Raises:
        Http404: If the newsletter with the given primary key does not exist.
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
    Rejects a newsletter based on its primary key (pk).
    This view function retrieves a newsletter object using the provided primary
    key (pk).
    It checks if the requesting user belongs to the "Editors" group.
    If the user is not an editor,
    it returns an HTTP 403 Forbidden response. If the user is an editor,
    it changes the status
    of the newsletter to "rejected" and saves the changes.
    Finally, it redirects to the "pending_newsletters" view.

    Args:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the newsletter to be rejected.

    Returns:
        HttpResponse: A redirect to the "pending_newsletters" view if the user
        is an editor.
        HttpResponseForbidden: An HTTP 403 Forbidden response if the user is
        not an editor.
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
    NewsletterListView
    This view inherits from Django's ListView and is used to display a list of
    newsletters.

    Attributes:
        model (Newsletter): The model that this view will operate on.
        template_name (str): The name of the template to render the list of
        newsletters.

    Methods:
        get_queryset(self):
            Returns a queryset of newsletters based on the user's group
            membership.
            - Editors, Journalists, and Readers can see all newsletters.
            - Other users can only see newsletters with the status "approved".
    """
    model = Newsletter
    template_name = "newsletter_list.html"

    def get_queryset(self):
        """
        Returns the queryset of newsletters based on the user's group
        membership.

        - Editors, Journalists, and Readers can see all newsletters.
        - Other users can only see newsletters with the status "approved".

        Returns:
            QuerySet: A queryset of newsletters filtered based on the user's
            group membership.
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
