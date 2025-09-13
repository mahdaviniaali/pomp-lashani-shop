from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.core.cache import cache
import json

from products.models import Product, ProductVariant
from payments.models import Order, OrderItem, Payment
from users.models import User
from carts.models import Cart, CartItem
from blog.models import Post
from .models import DashboardCache, ReportLog

User = get_user_model()


@staff_member_required
def dashboard_home(request):
    """صفحه اصلی داشبورد"""
    context = {
        'page_title': 'داشبورد مدیریت',
        'active_tab': 'overview'
    }
    return render(request, 'dashboard/home.html', context)


@staff_member_required
def sales_report(request):
    """گزارش فروش"""
    # دریافت پارامترهای فیلتر
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    status = request.GET.get('status', 'paid')  # پیش‌فرض: سفارشات پرداخت شده
    
    # تنظیم تاریخ پیش‌فرض (30 روز گذشته)
    if not date_from:
        date_from = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    if not date_to:
        date_to = timezone.now().strftime('%Y-%m-%d')
    
    # تبدیل تاریخ‌ها
    date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
    date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # فیلتر سفارشات
    orders_query = Order.objects.filter(
        created_at__date__range=[date_from_obj, date_to_obj]
    )
    
    if status != 'all':
        orders_query = orders_query.filter(status=status)
    
    # آمار کلی فروش - چک کردن هر دو وضعیت 'paid' و 'success' برای سفارشات موفق
    from django.db.models import Q
    successful_status_filter = Q(status='paid') | Q(status='success')
    paid_orders = orders_query.filter(successful_status_filter)
    total_orders = paid_orders.count()
    total_revenue = paid_orders.aggregate(total=Sum('total_price'))['total'] or 0
    avg_order_value = paid_orders.aggregate(avg=Avg('total_price'))['avg'] or 0
    
    # آمار روزانه فروش - فقط سفارشات پرداخت شده
    # استفاده از TruncDate برای سازگاری بهتر
    from django.db.models.functions import TruncDate
    
    daily_sales = paid_orders.annotate(
        day=TruncDate('created_at')
    ).values('day').annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('day')
    
    # Debug: چاپ داده‌ها
    daily_sales_list = list(daily_sales)
    print("Daily sales data:", daily_sales_list)
    
    # اگر داده‌ای نیست، نمونه‌ای بساز
    if not daily_sales_list:
        from datetime import date
        sample_data = []
        for i in range(7):
            day = date.today() - timedelta(days=i)
            sample_data.append({
                'day': day,
                'count': 0,
                'revenue': 0
            })
        daily_sales = sample_data
    else:
        daily_sales = daily_sales_list
    
    # پرفروش‌ترین محصولات - فقط سفارشات پرداخت شده
    top_products = OrderItem.objects.filter(
        order__in=paid_orders
    ).values('product_name').annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum(F('quantity') * F('price'))
    ).order_by('-total_sold')[:10]
    
    # آمار وضعیت سفارشات
    order_status_stats = orders_query.values('status').annotate(
        count=Count('id')
    )
    
    # آمار روش‌های پرداخت - فقط سفارشات پرداخت شده
    payment_method_stats = paid_orders.values('payment_method').annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    )
    
    context = {
        'page_title': 'گزارش فروش',
        'active_tab': 'sales',
        'date_from': date_from,
        'date_to': date_to,
        'status': status,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'daily_sales': json.dumps(list(daily_sales), default=str),
        'top_products': list(top_products),
        'order_status_stats': list(order_status_stats),
        'payment_method_stats': list(payment_method_stats),
    }
    
    return render(request, 'dashboard/sales_report.html', context)


@staff_member_required
def users_report(request):
    """گزارش کاربران"""
    # آمار کلی کاربران
    total_users = User.objects.count()
    active_users = User.objects.filter(available=True).count()
    verified_users = User.objects.filter(is_verified=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # کاربران جدید (30 روز گذشته)
    new_users = User.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # آمار ثبت‌نام روزانه
    daily_registrations = User.objects.extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('-day')[:30]
    
    # کاربران با بیشترین سفارش - چک کردن هر دو وضعیت 'paid' و 'success'
    # توجه: related_name='order' است، نه 'orders'
    successful_order_filter = Q(order__status='paid') | Q(order__status='success')
    top_customers = User.objects.annotate(
        order_count=Count('order', filter=successful_order_filter),
        total_spent=Sum('order__total_price', filter=successful_order_filter)
    ).filter(order_count__gt=0).order_by('-total_spent')[:10]
    
    # آمار تأیید کاربران
    verification_stats = {
        'verified': User.objects.filter(is_verified=True).count(),
        'unverified': User.objects.filter(is_verified=False).count(),
    }
    
    context = {
        'page_title': 'گزارش کاربران',
        'active_tab': 'users',
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'staff_users': staff_users,
        'new_users': new_users,
        'daily_registrations': json.dumps(list(daily_registrations), default=str),
        'top_customers': top_customers,
        'verification_stats': verification_stats,
    }
    
    return render(request, 'dashboard/users_report.html', context)


@staff_member_required
def products_report(request):
    """گزارش محصولات"""
    # آمار کلی محصولات
    total_products = Product.objects.count()
    available_products = Product.objects.filter(available=True).count()
    out_of_stock_products = Product.objects.filter(available=False).count()
    
    # محصولات پرفروش - استفاده از sold_count که در مدل Product موجود است
    top_selling_products = Product.objects.filter(
        sold_count__gt=0
    ).order_by('-sold_count')[:10]
    
    # آمار دسته‌بندی‌ها
    category_stats = Product.objects.values('category__title').annotate(
        count=Count('id'),
        total_sold=Sum('sold_count')
    ).order_by('-count')
    
    # آمار برندها
    brand_stats = Product.objects.values('brand__name').annotate(
        count=Count('id'),
        total_sold=Sum('sold_count')
    ).order_by('-count')
    
    # محصولات جدید (30 روز گذشته)
    new_products = Product.objects.filter(
        create_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # محصولات نیازمند تماس
    need_call_products = Product.objects.filter(need_to_call=True).count()
    
    context = {
        'page_title': 'گزارش محصولات',
        'active_tab': 'products',
        'total_products': total_products,
        'available_products': available_products,
        'out_of_stock_products': out_of_stock_products,
        'new_products': new_products,
        'need_call_products': need_call_products,
        'top_selling_products': top_selling_products,
        'category_stats': list(category_stats),
        'brand_stats': list(brand_stats),
    }
    
    return render(request, 'dashboard/products_report.html', context)


@staff_member_required
def inventory_report(request):
    """گزارش موجودی"""
    # آمار کلی موجودی
    total_variants = ProductVariant.objects.count()
    in_stock_variants = ProductVariant.objects.filter(stock__gt=0).count()
    out_of_stock_variants = ProductVariant.objects.filter(stock=0).count()
    low_stock_variants = ProductVariant.objects.filter(stock__lte=5, stock__gt=0).count()
    
    # محصولات با کمترین موجودی
    low_stock_products = ProductVariant.objects.filter(
        stock__lte=10, stock__gt=0
    ).select_related('product').order_by('stock')[:20]
    
    # محصولات تمام شده
    out_of_stock_products = ProductVariant.objects.filter(
        stock=0
    ).select_related('product')[:20]
    
    # آمار موجودی بر اساس دسته‌بندی
    category_inventory = ProductVariant.objects.values(
        'product__category__title'
    ).annotate(
        total_stock=Sum('stock'),
        variant_count=Count('id')
    ).order_by('-total_stock')
    
    context = {
        'page_title': 'گزارش موجودی',
        'active_tab': 'inventory',
        'total_variants': total_variants,
        'in_stock_variants': in_stock_variants,
        'out_of_stock_variants': out_of_stock_variants,
        'low_stock_variants': low_stock_variants,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'category_inventory': list(category_inventory),
    }
    
    return render(request, 'dashboard/inventory_report.html', context)


@staff_member_required
def blog_report(request):
    """گزارش وبلاگ"""
    # آمار کلی پست‌ها
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()
    draft_posts = Post.objects.filter(status='draft').count()
    archived_posts = Post.objects.filter(status='archived').count()
    
    # پست‌های جدید (30 روز گذشته)
    new_posts = Post.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # آمار نویسندگان
    author_stats = Post.objects.values('author__fullname').annotate(
        post_count=Count('id')
    ).order_by('-post_count')
    
    # پست‌های فعال
    active_posts = Post.objects.filter(available=True).count()
    
    context = {
        'page_title': 'گزارش وبلاگ',
        'active_tab': 'blog',
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'archived_posts': archived_posts,
        'new_posts': new_posts,
        'active_posts': active_posts,
        'author_stats': list(author_stats),
    }
    
    return render(request, 'dashboard/blog_report.html', context)


@staff_member_required
def ajax_dashboard_data(request):
    """داده‌های AJAX برای داشبورد"""
    data_type = request.GET.get('type', 'overview')
    
    if data_type == 'overview':
        # آمار کلی برای داشبورد اصلی
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)
        last_month = today - timedelta(days=30)
        
        # آمار فروش - چک کردن هر دو وضعیت 'paid' و 'success' برای سفارشات موفق
        from django.db.models import Q
        successful_status_filter = Q(status='paid') | Q(status='success')
        
        today_orders = Order.objects.filter(created_at__date=today).filter(successful_status_filter).count()
        yesterday_orders = Order.objects.filter(created_at__date=yesterday).filter(successful_status_filter).count()
        week_orders = Order.objects.filter(created_at__date__gte=last_week).filter(successful_status_filter).count()
        month_orders = Order.objects.filter(created_at__date__gte=last_month).filter(successful_status_filter).count()
        
        today_revenue = Order.objects.filter(
            created_at__date=today
        ).filter(successful_status_filter).aggregate(total=Sum('total_price'))['total'] or 0
        
        yesterday_revenue = Order.objects.filter(
            created_at__date=yesterday
        ).filter(successful_status_filter).aggregate(total=Sum('total_price'))['total'] or 0
        
        # آمار کاربران
        today_users = User.objects.filter(created_at__date=today).count()
        week_users = User.objects.filter(created_at__date__gte=last_week).count()
        month_users = User.objects.filter(created_at__date__gte=last_month).count()
        
        # آمار محصولات
        total_products = Product.objects.count()
        available_products = Product.objects.filter(available=True).count()
        
        data = {
            'orders': {
                'today': today_orders,
                'yesterday': yesterday_orders,
                'week': week_orders,
                'month': month_orders,
            },
            'revenue': {
                'today': today_revenue,
                'yesterday': yesterday_revenue,
            },
            'users': {
                'today': today_users,
                'week': week_users,
                'month': month_users,
            },
            'products': {
                'total': total_products,
                'available': available_products,
            }
        }
        
    elif data_type == 'sales_chart':
        # داده‌های نمودار فروش (7 روز گذشته)
        from django.db.models import Q
        successful_status_filter = Q(status='paid') | Q(status='success')
        
        days = []
        sales_data = []
        
        for i in range(7):
            date = (timezone.now() - timedelta(days=i)).date()
            orders_count = Order.objects.filter(
                created_at__date=date
            ).filter(successful_status_filter).count()
            revenue = Order.objects.filter(
                created_at__date=date
            ).filter(successful_status_filter).aggregate(total=Sum('total_price'))['total'] or 0
            
            days.append(date.strftime('%Y-%m-%d'))
            sales_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'orders': orders_count,
                'revenue': revenue
            })
        
        data = {
            'days': days,
            'sales': sales_data
        }
    
    return JsonResponse(data, safe=False)