from django.urls import path
from .views import *

app_name = 'blog'

urlpatterns = [
    path('' ,Blog.as_view() ,name='bloglist'),
    path('<slug>' , BlogDitail.as_view() , name='blogdetail'),
    path('post/<int:post_id>/addcomment/', Coments.as_view(), name='add_comment'),
    path('post/<int:post_id>/comments/', comment_list, name='comment_list')
]
