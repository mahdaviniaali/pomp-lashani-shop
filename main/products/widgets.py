from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class CropImageWidget(forms.FileInput):
    """
    Widget برای کراپ کردن تصاویر در فرم‌های Django
    """
    template_name = 'products/widgets/crop_image_widget.html'
    
    def __init__(self, target_size=None, *args, **kwargs):
        self.target_size = target_size or {'width': 800, 'height': 600}
        super().__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        context = {
            'name': name,
            'value': value,
            'target_size': self.target_size,
            'attrs': attrs or {},
        }
        return mark_safe(render_to_string(self.template_name, context))
    
    class Media:
        css = {
            'all': ('css/cropper.css',)
        }
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js',
            'js/cropper.js',
        )
