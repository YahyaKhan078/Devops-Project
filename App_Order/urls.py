from django.urls import path
from App_Order import views

app_name = 'App_Order'

urlpatterns = [
    path('add/<pk>/', views.add_to_cart, name='add'),
    path('cart/', views.cart_view, name='cart'),
    path('remove/<pk>/', views.remove_from_cart, name='remove'),
    path('increase/<pk>/', views.increase_cart, name='increase'),
    path('decrease/<pk>/', views.decrease_cart, name='decrease'),
    path('purchase/', views.purchase, name='purchase'),
    path('order-history/', views.order_history, name='order_history'),
    path('cart-sidebar-data/', views.cart_sidebar_data, name='cart_sidebar_data'),
]
