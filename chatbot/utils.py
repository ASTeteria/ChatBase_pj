from django.utils.html import strip_tags

def process_webhook_article(data):
    title = data.get('title', '')
    content = strip_tags(data.get('content', ''))
    content = content.strip()
    url = data.get('url', '')
    return {'title': title, 'content': content, 'url': url}