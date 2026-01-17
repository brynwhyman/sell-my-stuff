from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Category, Item


class ItemListView(ListView):
    """Display all items (both live and sold) with category filtering."""
    model = Item
    template_name = 'store/item_list.html'
    context_object_name = 'items'
    paginate_by = 12
    
    def get_queryset(self):
        """Show all items, with optional category filtering."""
        queryset = Item.objects.all().prefetch_related('images', 'category')
        
        # Filter by category if specified
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                category = Category.objects.get(slug=category_slug)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                pass  # Invalid category, show all items
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add categories to context for filter buttons."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('order', 'name')
        context['active_category'] = self.request.GET.get('category', '')
        return context


class ItemDetailView(DetailView):
    """Display details of a single item."""
    model = Item
    template_name = 'store/item_detail.html'
    context_object_name = 'item'
    
    def get_queryset(self):
        """Allow viewing all items."""
        return Item.objects.all().prefetch_related('images')
