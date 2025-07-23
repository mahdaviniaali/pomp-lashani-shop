from django import forms
from django.core.exceptions import ValidationError
from .models import User , Address

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="رمز عبور")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="تأیید رمز عبور")

    class Meta:
        model = User
        fields = ['fullname', 'email', 'phone_number', 'password', 'confirm_password']

    def clean(self):
        """ بررسی صحت رمز عبور و تأیید آن """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("رمز عبور و تأیید آن مطابقت ندارند.")

        return cleaned_data

    def save(self, commit=True):
        """ ذخیره کاربر با رمز عبور هش‌شده """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # هش کردن رمز عبور
        user.is_verified = False  # هنگام ثبت‌نام، کاربر تأیید نشده است
        user.available = True  # حساب کاربر فعال است مگر اینکه لاک شود

        if commit:
            user.save()

        return user


class AddressForm(forms.ModelForm):
    
    class Meta:
        model = Address
        fields = '__all__'
        exclude = ['user'] 


class AddUserInfoForm(forms.Form):
    fullname = forms.CharField(label='نام کامل', max_length=50, required=True)
    email = forms.EmailField(label='ایمیل', required=False)
    nationalcode = forms.CharField(label='کد ملی',max_length=11, required=False)



class AddUserInfoForm2(forms.Form):
    fullname = forms.CharField(label='نام کامل', max_length=50, required=True)
    email = forms.EmailField(label='ایمیل', required=False)
    nationalcode = forms.CharField(label='کد ملی',max_length=11, required=False)
    phone_number = forms.CharField(max_length=50, required=False)

class PhoneNumberForm(forms.Form):
    phone_number = forms.CharField(max_length=50, required=True)