from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.core.cache import cache
from products.models import Product
from categories.models import Category, Brand
from blog.models import Post
from taggit.models import Tag
from .form import ProductSearchForm
from users.models import Address
from .models import MainSlider, PromoCard, Partner, ExtraPhone


class Home(View):
    def get(self, request):
        # 1. کش اسلایدر اصلی (هفته‌ای یکبار آپدیت)
        main_slides = cache.get_or_set(
            'home_main_slides',
            MainSlider.objects.filter(is_active=True).order_by('order')[:5],  # حداکثر 5 اسلاید
            60 * 60 * 24 * 7  # 7 روز
        )

        # 2. کش کارت‌های تبلیغاتی (روزانه آپدیت) - بهینه‌سازی شده
        promo_cards = cache.get_or_set(
            'home_promo_cards_optimized',
            self._get_promo_cards_optimized(),
            60 * 60 * 24  # 1 روز
        )

        # 3. کش دسته‌بندی‌ها (هفته‌ای یکبار آپدیت) - بهینه‌سازی شده
        categories = cache.get_or_set(
            'home_categories_optimized',
            Category.objects.filter(available=True)
                           .select_related('parent')
                           .prefetch_related('children')
                           .order_by('title')[:10],
            60 * 60 * 24 * 7  # 7 روز
        )

        # کش برندها (هفته‌ای یکبار آپدیت) - بهینه‌سازی شده
        brands = cache.get_or_set(
            'home_brands_optimized',
            Brand.objects.filter(available=True)
                        .order_by('name')[:20],
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

        # 7. کش مقالات/خبرنامه (روزانه آپدیت) - بهینه‌سازی شده
        posts = cache.get_or_set(
            'home_posts_optimized',
            Post.objects.filter(available=True, status='published')
                       .select_related('author')
                       .order_by('-published_at')[:4],
            60 * 60 * 24  # 1 روز
        )


        # محتوای نهایی
        context = {
            'main_slides': main_slides,
            'promo_cards': promo_cards,
            'categories': categories,
            'brands': brands,
            'top_products': top_products,
            'random_tags': random_tags,
            'new_products': new_products,
            'posts': posts,        }
        return render(request, 'home.html', context)

    def _get_promo_cards_optimized(self):
        """
        بهینه‌سازی کوئری کارت‌های تبلیغاتی
        یک کوئری به جای 3 کوئری جداگانه
        """
        # یک کوئری برای دریافت همه کارت‌ها
        all_cards = PromoCard.objects.filter(is_active=True).order_by('order')
        
        # تقسیم‌بندی در Python به جای کوئری‌های جداگانه
        cards_dict = {
            'large': [],
            'medium': [],
            'small': []
        }
        
        for card in all_cards:
            if card.card_type in cards_dict and len(cards_dict[card.card_type]) < (2 if card.card_type == 'small' else 1):
                cards_dict[card.card_type].append(card)
        
        return cards_dict


class AboutUs (View):
    def get(self, request):
        # کش همکاران و برندها (هفته‌ای یکبار آپدیت)
        partners = cache.get_or_set(
            'home_partners',
            Partner.objects.filter(is_active=True).order_by('?')[:12],  # 12 همکار رندوم
            60 * 60 * 24 * 7  # 7 روز
        )
        content = {
            'partners': partners,
        }
        return render(request, 'about.html', content)
    
class ConectUs (View):
    def get (self , request):
        extra_phones = ExtraPhone.objects.filter(is_active=True)
        content = {
            'extra_phones': extra_phones,
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
        form = self.form_class(request.GET)  
        
        results = Product.objects.all()  
        if form.is_valid():  
            results = Product.objects.filter_and_order_by_params(request.GET)
        context = {
            'page_obj': results,
        }
        
        return render(request, self.template_name, context)










