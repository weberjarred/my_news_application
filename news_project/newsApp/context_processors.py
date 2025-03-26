from .models import Category


def news_categories(request):
    """
    Context processor that adds all news categories to the context.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        dict: A dictionary containing all categories with the key 'categories'.
    """
    return {"categories": Category.objects.all()}
