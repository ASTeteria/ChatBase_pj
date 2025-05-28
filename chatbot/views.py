from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Config, Article
from .utils import get_wordpress_articles
from django.conf import settings
from django.db.models import Q

# Главная страница
def home(request):
    config = Config.objects.filter(is_active=True).first()
    chatbot_id = config.chatbot_id if config else settings.CHATBOT_ID
    articles = Article.objects.all()
    return render(request, 'chatbot/home.html', {'chatbot_id': chatbot_id, 'articles': articles})

# Синхронизация статей
class WordPressSync(APIView):
    def post(self, request):
        wordpress_url = request.data.get('wordpress_url')
        if not wordpress_url:
            return Response({"error": "WordPress URL required"}, status=400)

        articles = get_wordpress_articles(wordpress_url)
        if not articles:
            return Response({"error": "No articles found"}, status=500)

        config, created = Config.objects.get_or_create(wordpress_url=wordpress_url)
        config.is_active = True
        config.save()

        for article in articles:
            Article.objects.update_or_create(
                config=config,
                url=article['url'],
                defaults={'title': article['title'], 'content': article['content']}
            )

        return Response({"articles_synced": len(articles)}, status=200)

# Поиск статей
class ArticleSearch(APIView):
    def post(self, request):
        query = request.data.get('query', '')
        if not query:
            return Response({"error": "Query required"}, status=400)

        # Ищем по заголовку или содержимому
        articles = Article.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

        if not articles:
            return Response({"response": "No articles found for your query."}, status=200)

        # Формируем ответ
        response = "Here are the articles found:\n"
        for article in articles:
            response += f"- {article.title}: {article.url}\n"

        return Response({"response": response}, status=200)