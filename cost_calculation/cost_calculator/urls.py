from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('homepage/', views.homepage, name='homepage'),
    path('calculate/', views.calculate_recipe, name='calculate'),
    # path('homepage/', views.homepage, name='homepage'),

]