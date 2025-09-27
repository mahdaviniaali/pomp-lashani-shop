import base64
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.shortcuts import render
from PIL import Image
import json

@csrf_exempt
@require_POST
def crop_image(request):
    """
    View برای پردازش کراپ تصویر
    دریافت data URL از JavaScript و تبدیل به فایل
    """
    try:
        data = json.loads(request.body)
        image_data = data.get('image_data')
        target_width = int(data.get('width', 800))
        target_height = int(data.get('height', 600))
        
        if not image_data:
            return JsonResponse({'error': 'تصویر ارسال نشده'}, status=400)
        
        # حذف header از data URL
        if ',' in image_data:
            header, encoded = image_data.split(',', 1)
            image_data = encoded
        
        # decode base64
        image_bytes = base64.b64decode(image_data)
        
        # ایجاد فایل از bytes
        image_file = ContentFile(image_bytes, name='cropped_image.jpg')
        
        # باز کردن تصویر با PIL برای بررسی
        image = Image.open(io.BytesIO(image_bytes))
        
        # بررسی اندازه
        if image.size != (target_width, target_height):
            # تغییر اندازه اگر لازم باشد
            image = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # تبدیل به bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=90)
            image_file = ContentFile(output.getvalue(), name='cropped_image.jpg')
        
        return JsonResponse({
            'success': True,
            'message': 'تصویر با موفقیت کراپ شد',
            'size': f'{target_width}x{target_height}',
            'file_size': len(image_bytes)
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'خطا در پردازش تصویر: {str(e)}'
        }, status=500)

def crop_form_view(request):
    """
    نمایش فرم کراپ تصویر
    """
    return render(request, 'products/crop_form.html')

def get_crop_sizes():
    """
    بازگرداندن اندازه‌های مختلف کراپ
    """
    return {
        'product_main': {'width': 800, 'height': 600, 'name': 'تصویر اصلی محصول'},
        'product_thumbnail': {'width': 200, 'height': 200, 'name': 'تصویر کوچک محصول'},
        'product_card': {'width': 300, 'height': 200, 'name': 'کارت محصول'},
        'product_detail': {'width': 600, 'height': 400, 'name': 'صفحه جزئیات'},
        'category_logo': {'width': 100, 'height': 100, 'name': 'لوگوی دسته‌بندی'},
        'brand_logo': {'width': 150, 'height': 100, 'name': 'لوگوی برند'},
    }
