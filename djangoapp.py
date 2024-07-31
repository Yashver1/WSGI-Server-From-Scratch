import sys
sys.path.insert(0, './django-app/mysite')
from mysite import wsgi


app = wsgi.application