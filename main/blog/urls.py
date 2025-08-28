from django.urls import path
from .views import *

app_name = 'blog'

urlpatterns = [
    path('' ,Blog.as_view() ,name='bloglist'),
    path('post/<post_id>/addcomment/', Coments.as_view(), name='add_comment'),
    path('post/<post_id>/comments/', comment_list, name='comment_list'),
    path('<pk>-<slug>/' , BlogDitail.as_view() , name='blogdetail'),
    path('<slug>/' , BlogDitail.as_view() , name='blogdetail_old')  # برای حفظ سازگاری با لینک‌های قدیمی
]
