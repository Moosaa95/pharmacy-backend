from django import forms

class OrderForm(forms.Form):
    cart = forms.JSONField()
    shipping_address = forms.JSONField()
    userbase = forms.IntegerField()
    total_price = forms.DecimalField(max_digits=10, decimal_places=2)
    status = forms.ChoiceField(choices=[("Processing", "Processing"), ("Shipped", "Shipped"), ("Delivered", "Delivered")])
    payment_info = forms.JSONField(required=False)
    # paid_at = forms.DateTimeField(widget=forms.HiddenInput(), required=False)
    delivered_at = forms.DateTimeField(widget=forms.HiddenInput(), required=False)


class AddPrescriptionImageForm(forms.Form):
    drug_id = forms.CharField(max_length=20)
    user_id = forms.CharField(max_length=20)
    prescription_image = forms.ImageField(required=False)
    

class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=20, required=False)
    last_name = forms.CharField(max_length=20, required=False)
    phone = forms.CharField(max_length=20, required=False)
    image = forms.ImageField(required=False)
    user_id = forms.CharField(max_length=20)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(max_length=20)
    new_password = forms.CharField(max_length=20)
    user_id = forms.CharField(max_length=20)

    
