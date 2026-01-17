from django.urls import path
from . import views
from . import webhooks

app_name = 'store'

urlpatterns = [
    path('', views.ItemListView.as_view(), name='item_list'),
    path('item/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('webhooks/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
]
