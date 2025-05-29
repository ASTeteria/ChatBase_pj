import requests
from django.utils.html import strip_tags

def get_wordpress_articles(wordpress_url):

    try:
        url = f"{wordpress_url}/wp-json/wp/v2/posts?per_page=100&type[]=post"
        response = requests.get(url)
        response.raise_for_status()
        posts = response.json()

        articles = []
        total_size = 0
        max_size = 400 * 1024

        for post in posts:
            title = post.get('title', {}).get('rendered', '')
            content = post.get('content', {}).get('rendered', '')
            content = strip_tags(content)
            url = post.get('link', '')
            size = len(content.encode('utf-8'))

            if total_size + size > max_size:
                break

            articles.append({'title': title, 'content': content, 'url': url})
            total_size += size

        print(f"Loaded {len(articles)} articles, {total_size} bytes")
        return articles
    except Exception as e:
        print(f"Error loading articles: {e}")
        return []