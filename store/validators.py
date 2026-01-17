"""
Validators for image uploads.
"""
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat


def validate_image_file_type(value):
    """Validate that uploaded file is an image."""
    valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if hasattr(value, 'content_type'):
        if value.content_type not in valid_types:
            raise ValidationError(
                f'File type not supported. Allowed types: {", ".join(valid_types)}'
            )


def validate_image_file_size(value):
    """Validate that uploaded file size is reasonable (max 5MB)."""
    max_size = 5 * 1024 * 1024  # 5MB in bytes
    if hasattr(value, 'size'):
        if value.size > max_size:
            raise ValidationError(
                f'File size too large. Maximum size is {filesizeformat(max_size)}.'
            )
