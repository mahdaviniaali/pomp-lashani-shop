from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.cache import cache
from products.models import Product
from categories.models import Category
from blog.models import Post
from taggit.models import Tag
from .form import ProductSearchForm
from users.models import Address
from .models import MainSlider, PromoCard


class Home(View):
    def get(self, request):
        # 1. کش اسلایدر اصلی (هفته‌ای یکبار آپدیت)
        main_slides = cache.get_or_set(
            'home_main_slides',
            MainSlider.objects.filter(is_active=True).order_by('order')[:5],  # حداکثر 5 اسلاید
            60 * 60 * 24 * 7  # 7 روز
        )

        # 2. کش کارت‌های تبلیغاتی (روزانه آپدیت)
        promo_cards = cache.get_or_set(
            'home_promo_cards',
            {
                'large': PromoCard.objects.filter(
                    card_type='large', 
                    is_active=True
                ).order_by('order')[:1],  # فقط 1 کارت بزرگ
                'medium': PromoCard.objects.filter(
                    card_type='medium', 
                    is_active=True
                ).order_by('order')[:1],  # فقط 1 کارت متوسط
                'small': PromoCard.objects.filter(
                    card_type='small', 
                    is_active=True
                ).order_by('order')[:2]  # 2 کارت کوچک
            },
            60 * 60 * 24  # 1 روز
        )

        # 3. کش دسته‌بندی‌ها (هفته‌ای یکبار آپدیت)
        categories = cache.get_or_set(
            'home_categories',
            Category.objects.all()[:10],  # فقط 10 مورد
            60 * 60 * 24 * 7  # 7 روز
        )

        # 4. کش پرفروش‌ترین محصولات (ساعتی آپدیت)
        top_products = cache.get_or_set(
            'top_products',
            Product.objects.order_by('-sold_count')
                          .with_related_for_home()
                          .filter(available=True)[:8],
            60 * 60  # 1 ساعت
        )

        # 5. کش تگ‌های رندوم (روزانه آپدیت)
        random_tags = cache.get_or_set(
            'home_random_tags',
            list(Tag.objects.order_by('?')[:10]),  # 10 تگ رندوم
            60 * 60 * 24  # 1 روز
        )

        # 6. کش جدیدترین محصولات (روزانه آپدیت)
        new_products = cache.get_or_set(
            'home_new_products',
            Product.objects.order_by('-create_at')
                          .with_related_for_home()
                          .filter(available=True)[:6],
            60 * 60 * 24  # 1 روز
        )

        # 7. کش مقالات/خبرنامه (روزانه آپدیت)
        posts = cache.get_or_set(
            'home_posts',
            Post.objects.all()[:3],  # فقط 3 مقاله
            60 * 60 * 24  # 1 روز
        )

        # محتوای نهایی
        context = {
            'main_slides': main_slides,
            'promo_cards': promo_cards,
            'categories': categories,
            'top_products': top_products,
            'random_tags': random_tags,
            'new_products': new_products,
            'posts': posts,
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










