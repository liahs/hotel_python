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
    path('', views.login.as_view(), name='login'),    
    path('overview/', views.overview.as_view(), name='overview'),
    path('dashboard/', views.home.as_view(), name='index'),
    path('logout/', views.logout.as_view(), name='logout'),
    path('add_user/', views.add_user.as_view(), name='add_user'),
    path('all_users/', views.all_users.as_view(), name='all_users'),
    path('delete_user/<id>', views.delete_user.as_view(), name='delete_user'),
    path('all_restaurants/', views.all_restaurants.as_view(), name='all_restaurants'),
    path('add_restaurant/', views.add_restaurant.as_view(), name='add_restaurant'),
    path('delete_rest/<id>', views.delete_rest.as_view(), name='delete_rest'),
    path('add_dish/', views.add_dish.as_view(), name='add_dish'),
    path('all_dishes/', views.all_dishes.as_view(), name='all_dishes'),
    path('delete_dish/<id>', views.delete_dish.as_view(), name='delete_dish'),
    path('add_review/', views.add_review.as_view(), name='add_review'),
    path('add_dish_review/', views.add_dish_review.as_view(), name='add_dish_review'),
    path('all_dish_review/', views.all_dish_reviews.as_view(), name='all_dish_reviews'),
    path('delete_dish_review/<id>', views.delete_dish_review.as_view(), name='delete_dish_review'),
    path('all_reviews/', views.all_reviews.as_view(), name='all_reviews'),
    path('delete_review/<id>', views.delete_review.as_view(), name='delete_review'),
    path('add_rating/', views.add_rating.as_view(), name='add_rating'),
    path('all_ratings/', views.all_ratings.as_view(), name='all_ratings'),
    path('delete_rating/<id>', views.delete_rating.as_view(), name='delete_rating'),
]
