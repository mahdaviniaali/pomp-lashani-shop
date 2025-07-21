from django import forms 
from .models import Product
from django_ckeditor_5.widgets import CKEditor5Widget




class PostAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget())

    class Meta:
        model = Product
        fields = '__all__'

    