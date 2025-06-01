import os
import sys
path = '/home/your-username/ChatBase_pj'
if path not in sys.path:
    sys.path.append(path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'chatbase_pj.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()