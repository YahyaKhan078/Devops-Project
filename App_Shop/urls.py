from django.urls import path
from . import views

app_name = 'App_Shop'

urlpatterns = [
    # 🏠 Home (all products)
    path('', views.home, name='home'),

    # 🔍 Search
    path('search/', views.search_products, name='search'),

    # 🔍 Product detail
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    #  Category wise products
    path('category/<int:category_id>/', views.products_by_category, name='by_category'),

    #  Age group filter
    path('age/<int:age_id>/', views.products_by_age, name='by_age'),

    #  Clothing type filter
    path('clothing/<int:type_id>/', views.products_by_clothing, name='by_clothing'),

    # About & Contact
    path('about/', views.about_us, name='about'),
    path('contact/', views.contact_us, name='contact'),
]