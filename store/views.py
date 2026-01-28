from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, FormView
from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from .models import Category, Item, ItemImage
from .forms import ItemCreateForm
from .stripe_service import create_payment_link_for_item


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


def check_upload_password(request):
    """Check if user has entered correct upload password."""
    return request.session.get('item_upload_authenticated', False)


class ItemCreateView(FormView):
    """Mobile-optimized view for creating items."""
    form_class = ItemCreateForm
    template_name = 'store/item_create.html'
    success_url = reverse_lazy('store:item_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Check password before allowing access."""
        if not check_upload_password(request):
            if request.method == 'POST' and 'password' in request.POST:
                password = request.POST.get('password', '')
                correct_password = getattr(settings, 'ITEM_UPLOAD_PASSWORD', '')
                if password == correct_password and correct_password:
                    request.session['item_upload_authenticated'] = True
                    return redirect(request.path)
                else:
                    messages.error(request, 'Incorrect password')
            return render(request, 'store/password_check.html')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Save item and images, create Stripe payment link."""
        try:
            # Save the item
            item = form.save(commit=False)
            # Ensure description is not empty (model requires it)
            if not item.description:
                item.description = 'No description provided'
            item.status = Item.STATUS_LIVE
            item.save()
        except Exception as e:
            messages.error(
                self.request,
                f'Error saving item: {str(e)}'
            )
            return self.form_invalid(form)
        
        # Handle image uploads
        images = self.request.FILES.getlist('images')
        if images:
            for index, image_file in enumerate(images):
                ItemImage.objects.create(
                    item=item,
                    image=image_file,
                    sort_order=index,
                    is_primary=(index == 0)  # First image is primary
                )
        
        # Create Stripe Payment Link
        try:
            payment_link_id, payment_link_url, product_id, price_id = \
                create_payment_link_for_item(item)
            item.stripe_payment_link_id = payment_link_id
            item.stripe_payment_link_url = payment_link_url
            item.stripe_product_id = product_id
            item.stripe_price_id = price_id
            item.save()
            messages.success(
                self.request,
                f'Item "{item.title}" created successfully! '
                f'<a href="{item.get_absolute_url()}" class="alert-link">View item</a>'
            )
        except Exception as e:
            messages.warning(
                self.request,
                f'Item created but Stripe payment link failed: {str(e)}. '
                f'You can create it manually in admin.'
            )
        
        return redirect('store:item_detail', pk=item.pk)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(
            self.request,
            'Please correct the errors below and try again.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        """Add categories to context."""
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('order', 'name')
        return context


class HowToBuyView(TemplateView):
    """Static page explaining how the site works and how to buy."""
    template_name = 'store/how_to_buy.html'
