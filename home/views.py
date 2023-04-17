import os
import re
from datetime import datetime

from core.models import Item, Category
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import generic

from djecommerce.settings.base import BASE_DIR
from .models import Post
from .form import CommentForm, ContactForm, WarrantyForm
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail, EmailMessage


# Create your views here.
def home(request):
    items = Item.objects.filter(label='F')
    categorys = Category.objects.all()[:3]
    return render(request, 'home.html', {'items': items, "categorys": categorys})

@login_required
def contact(request):
    new_contact = None
    template_name = 'contact.html'
    if request.method == 'POST':
        email = request.user.email
        contct_form = ContactForm(request.POST, request.FILES)
        if contct_form.is_valid():
            name = contct_form.cleaned_data.get('name')
            body = contct_form.cleaned_data.get('body')
            # email = contct_form.cleaned_data.get('email')
            attach = request.FILES.get('attachment', None)
            new_contact = contct_form.save(commit=False)
            if attach:
                save_name = name + "_" + email + "_" + attach.name
                save = os.path.join(os.path.join(BASE_DIR, 'media_root'), 'message_attachment')
                with open(os.path.join(save, save_name), 'wb+') as destination:
                    for chunk in attach.chunks():
                        destination.write(chunk)
                new_contact.attachment_address = os.path.join(save, save_name)
            new_contact.email = email
            new_contact.save()

            try:
                message = f"From: {name}\n" \
                          f"Email: {email}\n" \
                          f"Message: \n" \
                          f"{body}"
                mail = EmailMessage(subject="SKADE.US SERVICE", body=message, from_email=None, to=['service@skade.us'],
                                    reply_to=[email])
                if attach:
                    mail.attach_file(new_contact.attachment_address)
                mail.send()
                send_mail('Skade Message Service Confirmation',
                          'This is a confirmation of your SKADE customer service message request, a representative will contact you by email in 24 hours. Please do not reply to this message!',
                          None, [email], fail_silently=False)
                new_contact = f'Your Message is sent, a confirmation email has sent to your primary email address ({email}) shortly. We will contact you by email in 24 hours.'
            except:
                new_contact = 'Unable to send email. Please try again later or contact us by email at service@skade.us'
    else:
        contct_form = ContactForm()

    return render(request, template_name, {'new_contact': new_contact, 'contact_form': contct_form})


def about(request):
    return render(request, 'about.html', {})


def policy(request):
    return render(request, 'policy.html', {})


class PostList(generic.ListView):
    queryset = Post.objects.filter(status=1).order_by('-created_on')
    template_name = 'blog.html'


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'post_detail.html'


def post_detail(request, slug):
    template_name = 'post_detail.html'
    post_list = Post.objects.filter(status=1).order_by('-created_on')
    post = get_object_or_404(Post, slug=slug)
    comments = post.comments.filter(active=True)
    new_comment = None
    # Comment posted
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()



    else:
        comment_form = CommentForm()

    return render(request, template_name, {'post': post,
                                           'comments': comments,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form, 'post_list': post_list},
                  )


def warranty(request):
    template_name = 'warranty.html'
    new_warranty_request = None
    if request.method == 'POST':
        warranty_form = WarrantyForm(data=request.POST)
        if warranty_form.is_valid():
            # Save the comment to the database
            order_id = warranty_form.cleaned_data.get('order_number')
            pattern = '^\d{3}-\d{7}-\d{7}$'
            if re.fullmatch(pattern, order_id):
                name = warranty_form.cleaned_data.get('name')
                email = warranty_form.cleaned_data.get('email')
                warranty_form.save()
                try:
                    message = f"From: {name}\n" \
                              f"Email: {email}\n" \
                              f"Message: \n" \
                              f"{order_id}"
                    mail = EmailMessage(subject="SKADE.US Activate Warranty ", body=message, from_email=None,
                                        to=['service@skade.us'],
                                        reply_to=[email])
                    mail.send()
                    send_mail('Skade Message Service Confirmation',
                              'This is a confirmation of your SKADE warranty activation request, a representative will contact you by email in 24 hours. Please do not reply to this message!',
                              None, [email], fail_silently=False)
                    new_warranty_request = 'You request has been submitted. A confirmation will be sent to you once we confirm it.'
                except:
                    new_warranty_request = 'Unable to send email. Please try again later or contact us by email at service@skade.us'
            else:
                messages.info(request, "Please check your order number.")
                return redirect("home:warranty")
    else:
        warranty_form = WarrantyForm()
    return render(request, template_name, {
        'new_warranty_request': new_warranty_request,
        'warranty_form': warranty_form})


def find_id(request):
    return render(request, 'findid.html')
