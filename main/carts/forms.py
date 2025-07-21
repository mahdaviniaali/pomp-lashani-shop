from django import forms

class CartAddForm(forms.Form):
    product_id = forms.IntegerField(required=True)
    variant = forms.IntegerField(required=True)

class CartRemoveForm(forms.Form):
    product_id = forms.IntegerField(required=True)
    variant = forms.IntegerField(required=False)

class CartDecreaseForm(forms.Form):
    product_id = forms.IntegerField(required=True)
    variant = forms.IntegerField(required=False)

class CartClearForm(forms.Form):
    confirm = forms.BooleanField(required=False)