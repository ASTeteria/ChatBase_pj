from django.urls import path
from . import views

urlpatterns = [
    path('api/sync/', views.WordPressSync.as_view(), name='wordpress-sync'),
    path('api/search/', views.ArticleSearch.as_view(), name='article-search'),
    path('api/generate-agent/', views.GenerateAgent.as_view(), name='generate-agent'),
    path('api/delete-agent/', views.DeleteAgent.as_view(), name='delete-agent'),
    path('api/webhook/', views.WordPressWebhook.as_view(), name='webhook'),
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
]