from django.db import models

class Config(models.Model):
    wordpress_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.wordpress_url or "No URL"

class Article(models.Model):
    config = models.ForeignKey(Config, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=500)
    content = models.TextField()
    url = models.URLField(max_length=500, unique=True)

    def __str__(self):
        return self.title