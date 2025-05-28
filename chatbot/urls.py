from django.urls import path
from .views import home, WordPressSync, ArticleSearch

urlpatterns = [
    path('', home, name='home'),
    path('api/sync/', WordPressSync.as_view(), name='sync'),
    path('api/search/', ArticleSearch.as_view(), name='search'),
]