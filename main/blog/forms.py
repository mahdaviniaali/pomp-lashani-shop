from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Post

class PostAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content"].widget = CKEditor5Widget(
            attrs={"class": "django_ckeditor_5"}, 
            config_name="extends"
        )

    class Meta:
        model = Post
        fields = "__all__"