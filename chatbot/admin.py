from django.contrib import admin
from .models import Config, Article, Agent

admin.site.register(Config)
admin.site.register(Article)
admin.site.register(Agent)