"""
Forms for item creation.
"""
from django import forms
from .models import Item, Category, ItemImage
from decimal import Decimal


class ItemCreateForm(forms.ModelForm):
    """Form for creating items with mobile-optimized fields."""
    
    # Make description optional with default empty string
    description = forms.CharField(
        required=False,
        initial='',
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Optional description...',
            'class': 'form-input form-textarea',
        })
    )
    
    # Category is optional
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('order', 'name'),
        required=False,
        empty_label='No category',
        widget=forms.Select(attrs={
            'class': 'form-input form-select',
        })
    )
    
    class Meta:
        model = Item
        # Always store currency as NZD in code; no currency field on the form
        fields = ['title', 'description', 'category', 'price_amount']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Item title',
                'autofocus': True,
            }),
            'price_amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        """
        Save item with currency always set to NZD.
        Currency is not exposed on the form.
        """
        instance = super().save(commit=False)
        instance.currency = 'NZD'
        if commit:
            instance.save()
        return instance
