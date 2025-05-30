import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView
from .models import Config, Article
from .utils import process_webhook_article
from django.conf import settings
from django.db.models import Q

logger = logging.getLogger('chatbot')


class HomeView(TemplateView):
    template_name = 'home.html'


class WordPressSync(APIView):
    def post(self, request):
        logger.debug(f"Received sync request: {request.data}")

        api_key = request.headers.get('X-API-Key')
        if api_key != settings.WEBHOOK_API_KEY:
            logger.error("Invalid API key")
            return Response({"error": "Invalid API key"}, status=401)

        wordpress_url = request.data.get('wordpress_url')
        if not wordpress_url:
            logger.error("WordPress URL required")
            return Response({"error": "WordPress URL required"}, status=400)

        if not all(k in request.data for k in ['title', 'content', 'url']):
            logger.error("Missing required fields: title, content, url")
            return Response({"error": "Missing required fields"}, status=400)

        config, created = Config.objects.get_or_create(wordpress_url=wordpress_url)
        config.is_active = True
        config.save()

        article = process_webhook_article(request.data)
        Article.objects.update_or_create(
            config=config,
            url=article['url'],
            defaults={'title': article['title'], 'content': article['content']}
        )

        logger.info(f"Synced article: {article['title']}")
        return Response({"articles_synced": 1}, status=200)


class ArticleSearch(APIView):
    def post(self, request):
        query = request.data.get('query', '')
        if not query:
            logger.error("Query required")
            return Response({"error": "Query required"}, status=400)

        query_words = query.split()
        logger.debug(f"Search query words: {query_words}")

        query_filter = Q()
        for word in query_words:
            query_filter |= Q(title__icontains=word) | Q(content__icontains=word)

        articles = Article.objects.filter(query_filter)
        logger.info(f"Found {len(articles)} articles")

        if not articles:
            return Response({"response": "No articles found for your query."}, status=200)

        response = "Here are the articles found:\n"
        for article in articles:
            response += f"- {article.title}: {article.url}\n"

        return Response({"response": response}, status=200)