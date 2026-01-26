"""
Context processors for store app.
"""
from django.conf import settings


def upload_auth(request):
    """
    Add upload authentication status to template context.
    """
    return {
        'is_upload_authenticated': request.session.get('item_upload_authenticated', False)
    }
