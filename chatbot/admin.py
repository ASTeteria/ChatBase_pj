from django.contrib import admin
from .models import Config, Article

@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['wordpress_url', 'chatbot_id', 'is_active']

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'url']
