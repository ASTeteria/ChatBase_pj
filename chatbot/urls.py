from django.urls import path
from . import views

urlpatterns = [
    path('api/sync/', views.WordPressSync.as_view(), name='wordpress-sync'),
    path('api/search/', views.ArticleSearch.as_view(), name='article-search'),
    path('', views.HomeView.as_view(), name='home'),
]