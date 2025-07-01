from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('category/', views.category_view, name='category'),
    path('food/', views.food_view, name='food'),
    path('search/', views.search_view, name='search'),
    path('search/<str:slug>', views.search_view, name='search'),
    path('shopping/', views.shopping_view, name='shopping'),
]