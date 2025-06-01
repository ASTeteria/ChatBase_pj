import logging
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Config, Article, Agent
from .utils import process_article
from django.conf import settings
from django.db.models import Q

logger = logging.getLogger('chatbot')

class HomeView(TemplateView):
    template_name = 'home.html'

class RegisterView(TemplateView):
    template_name = 'registration/register.html'

    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info(f"User registered: {form.cleaned_data['username']}")
            return redirect('login')
        return render(request, self.template_name, {'form': form})

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agents = Agent.objects.filter(user=self.request.user, is_active=True)
        context['agents'] = agents
        return context

class GenerateAgent(APIView):
    def post(self, request):
        logger.debug(f"GenerateAgent request received: {request.user}")
        if not request.user.is_authenticated:
            logger.error("Unauthenticated user tried to generate agent")
            return Response({"error": "Authentication required"}, status=401)

        agent = Agent.objects.create(
            user=request.user,
            name=f"Agent for {request.user.username}"
        )
        logger.info(f"Generated agent: {agent.agent_id} for user: {request.user.username}")
        return Response({"agent_id": str(agent.agent_id)}, status=201)

class DeleteAgent(APIView):
    def post(self, request):
        logger.debug(f"DeleteAgent request received: {request.data}")
        if not request.user.is_authenticated:
            logger.error("Unauthenticated user tried to delete agent")
            return Response({"error": "Authentication required"}, status=401)

        agent_id = request.data.get('agent_id')
        if not agent_id:
            logger.error("Agent ID not provided")
            return Response({"error": "Agent ID required"}, status=400)

        try:
            agent = Agent.objects.get(agent_id=agent_id, user=request.user, is_active=True)
            agent.is_active = False
            agent.save()
            logger.info(f"Deleted agent: {agent_id} for user: {request.user.username}")
            return Response({"status": "Agent deleted"}, status=200)
        except Agent.DoesNotExist:
            logger.error(f"Agent not found: {agent_id}")
            return Response({"error": "Agent not found"}, status=404)

class WordPressWebhook(APIView):
    def post(self, request):
        logger.debug(f"Received webhook: {request.data}")

        api_key = request.headers.get('X-API-Key')
        if api_key != settings.WEBHOOK_API_KEY:
            logger.error("Invalid API key")
            return Response({"error": "Invalid API key"}, status=401)

        wordpress_url = request.data.get('wordpress_url')
        agent_id = request.data.get('agent_id')
        post_status = request.data.get('status')
        if not wordpress_url or not agent_id or post_status != 'publish':
            logger.error("Invalid webhook data")
            return Response({"error": "Invalid webhook data"}, status=400)

        try:
            agent = Agent.objects.get(agent_id=agent_id, is_active=True)
        except Agent.DoesNotExist:
            logger.error(f"Agent not found: {agent_id}")
            return Response({"error": "Agent not found"}, status=404)

        config, created = Config.objects.get_or_create(wordpress_url=wordpress_url)
        config.is_active = True
        config.save()

        article = process_article(request.data)
        Article.objects.update_or_create(
            config=config,
            agent=agent,
            url=article['url'],
            defaults={'title': article['title'], 'content': article['content']}
        )

        logger.info(f"Synced new article: {article['title']}")
        return Response({"status": "Article synced"}, status=200)

class WordPressSync(APIView):
    def post(self, request):
        logger.debug(f"Received sync request: {request.data}")

        api_key = request.headers.get('X-API-Key')
        if api_key != settings.WEBHOOK_API_KEY:
            logger.error("Invalid API key")
            return Response({"error": "Invalid API key"}, status=401)

        wordpress_url = request.data.get('wordpress_url')
        agent_id = request.data.get('agent_id')
        if not wordpress_url or not agent_id:
            logger.error("WordPress URL and Agent ID required")
            return Response({"error": "WordPress URL and Agent ID required"}, status=400)

        if not all(k in request.data for k in ['title', 'content', 'url']):
            logger.error("Missing required fields: title, content, url")
            return Response({"error": "Missing required fields"}, status=400)

        try:
            agent = Agent.objects.get(agent_id=agent_id, is_active=True)
        except Agent.DoesNotExist:
            logger.error(f"Agent not found: {agent_id}")
            return Response({"error": "Agent not found"}, status=404)

        config, created = Config.objects.get_or_create(wordpress_url=wordpress_url)
        config.is_active = True
        config.save()

        article = process_article(request.data)
        Article.objects.update_or_create(
            config=config,
            agent=agent,
            url=article['url'],
            defaults={'title': article['title'], 'content': article['content']}
        )

        logger.info(f"Synced article: {article['title']}")
        return Response({"articles_synced": 1}, status=200)

class ArticleSearch(APIView):
    def post(self, request):
        query = request.data.get('query', '')
        agent_id = request.data.get('agent_id', '')
        wordpress_url = request.data.get('wordpress_url', '')
        if not query or not agent_id or not wordpress_url:
            logger.error("Query, Agent ID, and WordPress URL required")
            return Response({"error": "Query, Agent ID, and WordPress URL required"}, status=400)

        try:
            agent = Agent.objects.get(agent_id=agent_id, is_active=True)
        except Agent.DoesNotExist:
            logger.error(f"Agent not found: {agent_id}")
            return Response({"error": "Agent not found"}, status=404)

        # Сохраняем найденные статьи
        articles_data = request.data.get('articles', [])
        config, _ = Config.objects.get_or_create(wordpress_url=wordpress_url)
        for article in articles_data:
            Article.objects.update_or_create(
                config=config,
                agent=agent,
                url=article['url'],
                defaults={'title': article['title'], 'content': article['content']}
            )
            logger.info(f"Synced searched article: {article['title']}")

        # Получаем статьи для контекста
        articles = Article.objects.filter(agent=agent, config=config)
        if not articles:
            return Response({"response": "No articles found for your query."}, status=200)

        try:
            ai_response = self.query_ai(query, articles)
            return Response({"response": ai_response}, status=200)
        except Exception as e:
            logger.error(f"AI query error: {str(e)}")
            return Response({"error": "AI processing error"}, status=500)

    def query_ai(self, query, articles):
        context = "\n".join([f"Title: {a.title}\n{a.url}\n{a.content[:200]}" for a in articles])
        headers = {
            'Authorization': f'Bearer {settings.AI_API_KEY}',
            'Content-Type': 'application/json',
        }
        data = {
            'model': 'grok-3',
            'messages': [
                {
                    'role': 'system',
                    'content': (
                        'You are an AI assistant for a WordPress site. Your task is to find relevant articles based on user queries. '
                        'Return a concise response with article titles and URLs. If no articles match, say so.'
                    ),
                },
                {
                    'role': 'user',
                    'content': f"Find articles for query: {query}\n\nAvailable articles:\n{context}",
                },
            ],
        }

        response = requests.post(settings.AI_API_URL, json=data, headers=headers)
        if response.status_code != 200:
            logger.error(f"AI API error: {response.text}")
            raise Exception("AI API error")

        ai_data = response.json()
        return ai_data.get('choices', [{}])[0].get('message', {}).get('content', '')