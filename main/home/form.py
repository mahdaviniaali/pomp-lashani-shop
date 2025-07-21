from django import forms




class ProductSearchForm(forms.Form):
    search = forms.CharField(label='جستجو', max_length=100)

    