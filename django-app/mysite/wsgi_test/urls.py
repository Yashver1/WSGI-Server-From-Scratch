from django.urls import path 

from wsgi_test import views 

urlpatterns = [
    path("",views.home, name="home"),
    path("hello/",views.hello_world, name="hello")
]