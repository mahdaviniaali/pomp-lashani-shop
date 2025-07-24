from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from products.models import Product
from categories.models import Category
from blog.models import Post
from taggit.models import Tag
from .form import ProductSearchForm
from users.models import Address

class Home(View):
    def get(self, request):
        # 1. کش دسته‌بندی‌ها (هفته‌ای یکبار آپدیت)
        categories = cache.get_or_set(
            'home_categories',
            Category.objects.all()[:10],  # فقط 10 مورد
            60 * 60 * 24 * 7  # 7 روز (هفته‌ای یکبار)
        )

        # پر فروش ترین محصولات
        top_products = cache.get_or_set('top_products',Product.objects.order_by('-sold_count').with_related_for_home().filter(available=True)[:8],5)

        # 3. کش تگ‌های رندوم (روزانه آپدیت)
        random_tags = cache.get_or_set(
            'home_random_tags',
            list(Tag.objects.order_by('?')[:10]),  # 10 تگ رندوم
            60 * 60 * 24  # 1 روز
        )

        # 4. کش جدیدترین محصولات (شرطی با تنظیمات)
       
        new_products = Product.objects.order_by('-create_at').with_related_for_home().filter(available=True)[:6]
        cache.set('home_new_products', new_products, 60 * 60 * 24)  # 1 روز
        

        # 5. کش خبرنامه (شرطی با تنظیمات)
        
        post = Post.objects.all()
        cache.set('Post', post, 60 * 60 * 24)  # 1 روز
       

        # محتوای نهایی
        context = {
            'categories': categories,
            'top_products': top_products,
            'random_tags': random_tags,
            'new_products': new_products,
            'post': post,
        }
        
        return render(request, 'home.html', context)





class HomeSample(View):
    def get (self, request):
        
        context = {
           
        }
        return render(request, 'home2.html', context)

class AboutUs (View):
    def get (self , request):

        content = {

        }
        return render(request,'about.html',content)
    
class ConectUs (View):
    def get (self , request):

        content = {

        }
        return render(request,'contact.html',content)
    
class FAQ (View):
    def get (self , request):

        content = {

        }
        return render(request,'faq.html',content)
    



#=========
#partials
#=========

class UserAddressListView(LoginRequiredMixin, View):
    def get (self, request):
        user = request.user
        address_id = request.GET.get('address_id')
        print(address_id)
        if address_id:
            print('s')
            address = Address.objects.get(id=address_id, user=user)
        else:
            print('l')
            address = Address.objects.filter(user=user).first()

        if address:
            return render(request, 'partials/address_list.html', {'addresses': address})
        else:
            return render(request, 'partials/no_address.html')
        

#user info
class UserInfoView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        return render(request, 'partials/user_info.html', {'user':user})
    



# ویو بلا استفاده برای مواقع ضروری
class ProductSearch(View):
    form_class = ProductSearchForm
    template_name = 'products.html'  # مشخص کردن نام تمپلیت

    def get(self, request):
        form = self.form_class(request.GET)  # اصلاح: استفاده از self.form_class و GET data
        
        results = Product.objects.all()  # مقدار پیش‌فرض وقتی جستجو انجام نشده
        
        if form.is_valid():  # بررسی اعتبار فرم
            query = form.cleaned_data.get('search')  # استفاده از .get() برای جلوگیری از KeyError
            if query:
                results = Product.objects.filter(title__icontains=query)
                print(f"Search query: {results}")  # برای دیباگینگ
        
        context = {
            'page_obj': results,
        }
        
        return render(request, self.template_name, context)










