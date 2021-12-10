"""finalproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name='login'),
    path('dashboard/', views.home, name='index'),
    path('logout/', views.logout, name='logout'),
    path('add_user/', views.add_user, name='add_user'),
    path('all_users/', views.all_users, name='all_users'),
    path('delete_user/<id>', views.delete_user, name='delete_user'),
    path('all_restaurants/', views.all_restaurants, name='all_restaurants'),
    path('add_restaurant/', views.add_restaurant, name='add_restaurant'),
    path('delete_rest/<id>', views.delete_rest, name='delete_rest'),
    path('add_dish/', views.add_dish, name='add_dish'),
    path('all_dishes/', views.all_dishes, name='all_dishes'),
    path('delete_dish/<id>', views.delete_dish, name='delete_dish'),
    path('add_review/', views.add_review, name='add_review'),
    path('all_reviews/', views.all_reviews, name='all_reviews'),
    path('delete_review/<id>', views.delete_review, name='delete_review'),
    path('add_rating/', views.add_rating, name='add_rating'),
    path('all_ratings/', views.all_ratings, name='all_ratings'),
    path('delete_rating/<id>', views.delete_rating, name='delete_rating'),
    path('overview/', views.overview, name='overview'),
]
