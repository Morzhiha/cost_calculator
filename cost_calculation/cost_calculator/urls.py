from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .forms import AuthForm

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='registration/login.html',
        authentication_form=AuthForm,
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/reset_password/', views.register, name='reset_password'),
    path('accounts/profile/', views.profile, name='profile'),

    path('products/', views.product_catalog, name='products'),
    path('products/create/', views.create_product, name='create_product'),
    path('products/update/<int:pk>/', views.update_product, name='update_product'),
    path('products/delete/<int:pk>/', views.delete_product, name='delete_product'),
    path('products/check-exists/', views.check_product_exists, name='check-product-exists'),
    path('recipes/', views.recipe_catalog, name='recipes'),
    path('recipes/create/', views.recipe_edit, name='recipe_create'),
    path('recipes/<int:recipe_id>/', views.recipe_edit, name='recipe_edit'),
    path('recipes/delete/<int:recipe_id>/', views.recipe_delete, name='recipe_delete'),

]