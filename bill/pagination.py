from rest_framework.pagination import PageNumberPagination

class CustomBillPagination(PageNumberPagination):
    """Custom pagination for the Bill model."""
    page_size = 10  # Default number of items per page
    page_size_query_param = 'page_size'  # Allow clients to set the page size via query params
    max_page_size = 50  # Maximum page size allowed