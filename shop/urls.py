from django.urls import path
from . import views

urlpatterns = [
  path('', views.login_view, name='login'),
  path('products/', views.products_list, name='products_list'),
  path('products/add/', views.product_edit, name='products_add'),
  path('products/edit/<int:pk>/', views.product_edit, name='product_edit'),
]