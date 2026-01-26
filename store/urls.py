from django.urls import path
from . import views
from . import webhooks

app_name = 'store'

urlpatterns = [
    path('', views.ItemListView.as_view(), name='item_list'),
    path('item/<int:pk>/', views.ItemDetailView.as_view(), name='item_detail'),
    path('how-to-buy/', views.HowToBuyView.as_view(), name='how_to_buy'),
    path('add-item/', views.ItemCreateView.as_view(), name='item_create'),
    path('webhooks/stripe/', webhooks.stripe_webhook, name='stripe_webhook'),
]
