from django.core.paginator import Paginator

def get_paginated_queryset(queryset, per_page, request):
    """Helper function for pagination."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)