import uuid
from django.db import models
from django.contrib.auth.models import User

class Config(models.Model):
    wordpress_url = models.URLField(max_length=256, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.wordpress_url or "No URL"

class Agent(models.Model):
    agent_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, default="PsibotChat Agent")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.agent_id})"

class Article(models.Model):
    config = models.ForeignKey(Config, on_delete=models.CASCADE, null=True)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=256)
    content = models.TextField()
    url = models.URLField(max_length=256, unique=True)

    def __str__(self):
        return self.title