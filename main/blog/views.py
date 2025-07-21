from django.shortcuts import render
from django.views import View
from .models import Post, Comment
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

import logging

logger = logging.getLogger(__name__)

# Create your views here.
class Blog (View):
    def get (self ,request):
        post = Post.objects.all()
        content= {
            'posts' : post

        }
        return render(request ,'blog.html' ,content )
    
class BlogDitail (View):
    def get (self ,request ,slug):
        post = Post.objects.get(slug=slug)
        content= {
            'post' : post
        }
        return render(request ,'single-blog.html' ,content )
    


class Coments (View):

    def post(self, request, post_id):
        if not request.user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'نیاز به ورود به سیستم'}, status=403)
        
        body = request.POST.get('body', '').strip()
        if not body:
            return JsonResponse({'status': 'error', 'message': 'متن نظر نمی‌تواند خالی باشد'}, status=400)
        
        comment = Comment.objects.create(
            post_id=post_id,
            user=request.user,
            content=body
        )
        
        
        
        return HttpResponse(body)
    

@require_http_methods(["GET"])
def comment_list(request, post_id):
    comments = Comment.objects.filter(post_id=post_id, available=True)
    print(comments)
    return render(request, 'comment_list.html', {
        'comments': comments
    })