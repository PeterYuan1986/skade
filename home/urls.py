from django.urls import path
from .views import *

app_name = 'home'
urlpatterns = [
    path('', home, name='home'),
    path('contact/', contact, name='contact'),
    path('about/', about, name='about'),
    path('policy/', policy, name='policy'),
    path('blog/', PostList.as_view(), name='blog'),
    # path('blog/<slug:slug>', PostDetail.as_view(), name='post_detail'),
    path('blog/<slug:slug>', post_detail, name='post_detail')
]
