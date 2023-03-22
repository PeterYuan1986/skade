from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from localflavor.us.forms import USZipCodeField, USStateField, USStateSelect
from core.models import Comment

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)


class SearchForm(forms.Form):
    search = forms.CharField(label='search', max_length=20)


class CheckoutForm(forms.Form):
    shipping_first_name = forms.CharField(required=False)
    shipping_last_name = forms.CharField(required=False)
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_city = forms.CharField(required=False)

    shipping_state = USStateField(required=False, widget=USStateSelect(attrs={
        'class': 'custom-select d-block w-100',
    }))
    shipping_zip = USZipCodeField(required=False)
    billing_first_name = forms.CharField(required=False)
    billing_last_name = forms.CharField(required=False)
    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_city = forms.CharField(required=False)

    billing_state = USStateField(required=False, widget=USStateSelect(attrs={
        'class': 'custom-select d-block w-100',
    }))
    billing_zip = USZipCodeField(required=False)
    same_billing_address = forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)
    use_default_billing = forms.BooleanField(required=False)
    #
    # payment_option = forms.ChoiceField(
    #     widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
