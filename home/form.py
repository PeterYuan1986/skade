from .models import Comment, Contact
from django import forms
from django.contrib.auth.decorators import login_required


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')


class ContactForm(forms.ModelForm):
    name = forms.Textarea()

    class Meta:
        model = Contact
        fields = ('name', 'email', 'body', 'attachment')
