from django.db import models

class Config(models.Model):
    wordpress_url = models.URLField(max_length=200)
    chatbot_id = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Config for {self.wordpress_url}"

class Article(models.Model):
    config = models.ForeignKey(Config, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    content = models.TextField()

    def __str__(self):
        return self.title