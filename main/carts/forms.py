from django import forms
import re

class CartAddForm(forms.Form):
    product_id = forms.IntegerField(required=True)
    variant = forms.IntegerField(required=True)

class CartRemoveForm(forms.Form):
    product_id = forms.IntegerField(required=True)
    variant = forms.IntegerField(required=True)

class CartDecreaseForm(forms.Form):
    product_id = forms.IntegerField(required=True)
    variant = forms.IntegerField(required=True)

class CartClearForm(forms.Form):
    confirm = forms.BooleanField(required=False)

class CartShebaForm(forms.Form):
    sheba_number = forms.CharField(
        max_length=26,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'IR123456789012345678901234',
            'maxlength': '26',
            'pattern': 'IR[0-9]{22}',
            'title': 'شماره شبا باید با IR شروع شود و 24 کاراکتر باشد'
        }),
        help_text="شماره شبا 24 رقمی (مثال: IR123456789012345678901234)"
    )
    
    def clean_sheba_number(self):
        sheba = self.cleaned_data.get('sheba_number')
        if not sheba:
            return sheba
        
        # پاک کردن فاصله و کاراکترهای اضافی
        cleaned = sheba.replace(' ', '').replace('-', '').replace('_', '').upper()
        
        # بررسی طول
        if len(cleaned) != 24:
            raise forms.ValidationError("شماره شبا باید دقیقاً 24 کاراکتر باشد")
        
        # بررسی شروع با IR
        if not cleaned.startswith('IR'):
            raise forms.ValidationError("شماره شبا باید با IR شروع شود")
        
        # بررسی اینکه بقیه کاراکترها عدد باشند
        if not cleaned[2:].isdigit():
            raise forms.ValidationError("بعد از IR باید فقط عدد باشد")
        
        return cleaned