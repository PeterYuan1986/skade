import json
import math
import random
import string

import stripe
from django.conf import settings
from django.conf.global_settings import MEDIA_URL
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, View
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, SearchForm, CommentForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Category

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='B',
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_first_name = form.cleaned_data.get(
                        'shipping_first_name')
                    shipping_last_name = form.cleaned_data.get(
                        'shipping_last_name')
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_city = form.cleaned_data.get(
                        'shipping_city')
                    shipping_state = form.cleaned_data.get(
                        'shipping_state')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form(
                            [shipping_first_name, shipping_last_name, shipping_address1, shipping_city, shipping_state,
                             shipping_zip]):
                        shipping_address = Address(user=self.request.user,
                                                   first_name=shipping_first_name,
                                                   last_name=shipping_last_name,
                                                   street_address=shipping_address1,
                                                   apartment_address=shipping_address2,
                                                   city=shipping_city,
                                                   state=shipping_state,
                                                   zip=shipping_zip,
                                                   address_type='S')
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            address_qs = Address.objects.filter(
                                user=self.request.user,
                                address_type='S',
                                default=True
                            )
                            if address_qs.exists():
                                pre_default_shipping_address = address_qs[0]
                                pre_default_shipping_address.default = False
                                pre_default_shipping_address.save()
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")
                        return redirect('core:checkout')

                use_default_billing = form.cleaned_data.get(
                    'use_default_billing')
                same_billing_address = form.cleaned_data.get(
                    'same_billing_address')

                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.default = False
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the defualt billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default billing address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new billing address")
                    billing_first_name = form.cleaned_data.get(
                        'billing_first_name')
                    billing_last_name = form.cleaned_data.get(
                        'billing_last_name')
                    billing_address1 = form.cleaned_data.get(
                        'billing_address')
                    billing_address2 = form.cleaned_data.get(
                        'billing_address2')
                    billing_city = form.cleaned_data.get(
                        'billing_city')
                    billing_state = form.cleaned_data.get(
                        'billing_state')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form(
                            [billing_first_name, billing_last_name, billing_address1, billing_city, billing_state,
                             billing_zip]):
                        billing_address = Address(user=self.request.user,
                                                  first_name=billing_first_name,
                                                  last_name=billing_last_name,
                                                  street_address=billing_address1,
                                                  apartment_address=billing_address2,
                                                  city=billing_city,
                                                  state=billing_state,
                                                  zip=billing_zip,
                                                  address_type='B'
                                                  )
                        billing_address.save()

                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get(
                            'set_default_billing')
                        if set_default_billing:
                            address_qs = Address.objects.filter(
                                user=self.request.user,
                                address_type='B',
                                default=True
                            )
                            if address_qs.exists():
                                pre_default_billing_address = address_qs[0]
                                pre_default_billing_address.default = False
                                pre_default_billing_address.save()
                            billing_address.default = True
                            billing_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required billing address fields")
                        return redirect('core:checkout')
                itms = order.items.all()
                line_items = [{'price': item.item.price_id, 'quantity': item.quantity} for item in
                              itms]
                if order.coupon:
                    discounts = [{'coupon': order.coupon.coupon_id}]
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        discounts=discounts,
                        success_url=self.request.build_absolute_uri(
                            reverse('core:order-success')) + '?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url=self.request.build_absolute_uri(reverse('core:order-summary')),
                        customer_creation="if_required"
                    )
                else:
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=line_items,
                        mode='payment',
                        success_url=self.request.build_absolute_uri(
                            reverse('core:order-success')) + '?session_id={CHECKOUT_SESSION_ID}',
                        cancel_url=self.request.build_absolute_uri(reverse('core:order-summary')),
                        customer_creation="if_required"
                    )
                if order.checkout_session:
                    stripe.checkout.Session.expire(order.checkout_session, )
                order.checkout_session = session['id']
                order.save()

                return redirect(session.url)

                # payment_option = form.cleaned_data.get('payment_option')
                #
                # if payment_option == 'S':
                #     return redirect('core:payment', payment_option='stripe')
                # elif payment_option == 'P':
                #     return redirect('core:payment', payment_option='paypal')
                # else:
                #     messages.warning(
                #         self.request, "Invalid payment option selected")
                #     return redirect('core:checkout')
            else:
                    messages.info(
                        self.request,
                        "Please fill in the zip code in the format of XXXXX or XXXXX-XXXX")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


def order_success(request):
    try:
        session_id = request.GET.get('session_id')
        session = stripe.checkout.Session.retrieve(session_id)
        if session['payment_status'] == 'paid':
            # customer = stripe.Customer.retrieve(session.customer)
            try:
                order_qs = Order.objects.get(user=request.user, ordered=False)
                order_qs.ordered = True
                for order_items in order_qs.items.all():
                    order_items.delete()
                line_items = stripe.checkout.Session.list_line_items(session_id)['data']
                for item in line_items:
                    order_items = OrderItem.objects.create(user=request.user,
                                                           ordered=True,
                                                           item=Item.objects.get(price_id=item['price']["id"]),
                                                           quantity=item['quantity'],
                                                           ordered_price=item['price']["unit_amount"] / 100,
                                                           tax=item['amount_tax'], )
                    order_items.save()
                    order_qs.items.add(order_items)
                payment = Payment.objects.create(stripe_charge_id=session_id,
                                                 user=request.user, amount=session['amount_total'])
                payment.save()
                order_qs.payment = payment
                order_qs.save()
                return render(request, 'order_success.html', {'object': order_qs, 'ordernumber': session_id[-13:]})
            except ObjectDoesNotExist:
                messages.warning(request, "Your order page is expired, please check your order in order history page.")
                return redirect("core:order-history")
        else:
            messages.warning(request, "You do not have an active order")
            return redirect("core:order-summary")
    except:
        messages.warning(request, "Your order page is expired, please check your order in order history page.")
        return redirect("core:order-history")


def order_failed(request):
    return render(request, 'order_failed.html')


class OrderHistoryView(View):
    def get(self, *args, **kwargs):
        obeject = Order.objects.filter(user=self.request.user, ordered=True)
        return render(self.request, 'order_history.html', {'objects': obeject})


@csrf_exempt
def stripe_webhook(request):
    print('WEBHOOK!')
    # You can find your endpoint's secret in your webhook settings
    endpoint_secret = 'whsec_Xj8wBk2qiUcjDEmYu5kfKkOrJCJ5UUjW'

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)
        line_items = stripe.checkout.Session.list_line_items(session['id'], limit=1)
        print(line_items)

    return HttpResponse(status=200)


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, "You have not added a billing address")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


def shop(request, category='All'):
    search = ''
    items_per_page = 9
    form = SearchForm()
    categorys = Category.objects.all()
    if request.method == 'POST':
        searchform = SearchForm(request.POST)
        if searchform.is_valid():
            search = searchform.cleaned_data['search']

        if category != 'All':
            category = Category.objects.get(slug=category)
            object_list = Item.objects.filter(category=category.id,
                                              title__contains=search) | Item.objects.filter(
                category=category.id, slug__contains=search) | Item.objects.filter(
                category=category.id, sku__contains=search) | Item.objects.filter(category=category.id,
                                                                                  information__contains=search) | Item.objects.filter(
                category=category.id, description1__contains=search) | Item.objects.filter(
                category=category.id, description2__contains=search) | Item.objects.filter(
                category=category.id, description3__contains=search) | Item.objects.filter(
                category=category.id, description4__contains=search) | Item.objects.filter(
                category=category.id, description5__contains=search)
            category = category.slug
        else:
            object_list = Item.objects.filter(
                title__contains=search) | Item.objects.filter(
                slug__contains=search) | Item.objects.filter(
                sku__contains=search) | Item.objects.filter(
                information__contains=search) | Item.objects.filter(
                description1__contains=search) | Item.objects.filter(
                description2__contains=search) | Item.objects.filter(
                description3__contains=search) | Item.objects.filter(
                description4__contains=search) | Item.objects.filter(
                description5__contains=search)
        return render(request, 'shop.html',
                      {'categorys': categorys, 'category': category, 'object_list': object_list, 'form': form,
                       'is_paginated': False})
    else:
        if category != 'All':
            category = Category.objects.get(slug=category)
            object_list = Item.objects.filter(category=category.id)
            category = category.slug
        else:
            object_list = Item.objects.all()
        paginator = Paginator(object_list, items_per_page)  # Show 9 items per page.
        pages = math.ceil(object_list.count() / items_per_page)
        page_number = int(request.GET.get('page')) if request.GET.get('page') else 1
        page_obj = paginator.get_page(page_number)
        return render(request, 'shop.html',
                      {'categorys': categorys, 'category': category, 'object_list': page_obj, 'form': form,
                       'curpage': page_number, 'pages': list(range(1, pages + 1)), 'is_paginated': True})


class HomeView(ListView):
    model = Item
    paginate_by = 8
    template_name = "shop.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


def item_detail(request, slug):
    items_per_page = 4
    template_name = 'product.html'
    object = get_object_or_404(Item, slug=slug)
    comments = object.comments.filter(active=True)
    new_comment = None

    # Comment posted

    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        rating = request.POST.get('rating') if request.POST.get('rating') else 0
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.item = object
            # Save the comment to the database
            new_comment.stars = rating
            new_comment.save()
    else:
        paginator = Paginator(comments, items_per_page)  # Show 9 items per page.
        pages = math.ceil(comments.count() / items_per_page)
        page_number = request.GET.get('page')
        if page_number:
            page_number = int(page_number.split('/')[0])
        else:
            page_number = 1
        page_obj = paginator.get_page(page_number)
        comment_form = CommentForm()
    return render(request, template_name, {'object': object,
                                           'comments': page_obj,
                                           'new_comment': new_comment,
                                           'comment_form': comment_form,
                                           'curpage': page_number,
                                           "pages": list(range(1, pages + 1))},
                  )


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    if request.method == 'POST':
        amount = request.POST.get('product-quanity')
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False,
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += int(amount)
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                # return redirect("core:order-summary")
            else:
                order_item.quantity = int(amount)
                order_item.save()
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
            order.ordered_date = datetime.now()
            # return redirect("core:order-summary")
        else:
            order = Order.objects.create(user=request.user,
                                         ordered_date=datetime.now())
            order_item.quantity = int(amount)
            order_item.save()
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            # return redirect("core:order-summary")
        order.save()
        return redirect(f"/#{slug}")
    elif request.method == 'GET':
        if request.GET.get('product-quanity'):
            amount = request.GET.get('product-quanity')
        else:
            amount = 1
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += int(amount)
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                # return redirect("core:order-summary")
            else:
                order_item.quantity = int(amount)
                order_item.save()
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
                # return redirect("core:order-summary")
            order.ordered_date = datetime.now()
        else:
            order = Order.objects.create(user=request.user,
                                         ordered_date=datetime.now())
            order_item.quantity = int(amount)
            order_item.save()
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            # return redirect("core:order-summary")
        order.save()
        return redirect(f"/product/{slug}")
    else:
        order_item, created = OrderItem.objects.get_or_create(
            item=item,
            user=request.user,
            ordered=False
        )
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item__slug=item.slug).exists():
                order_item.quantity += 1
                order_item.save()
                messages.info(request, "This item quantity was updated.")
                # return redirect("core:order-summary")
            else:
                order.items.add(order_item)
                messages.info(request, "This item was added to your cart.")
                # return redirect("core:order-summary")
            order.ordered_date = datetime.now()
        else:
            order = Order.objects.create(user=request.user, ordered_date=datetime.now())
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            # return redirect("core:order-summary")
        order.save()
        return redirect(f"/shop/#{slug}")


@login_required
def buy_now(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            order.ordered_date=datetime.now()
            order.save()
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            order.ordered_date=datetime.now()
            order.save()
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        order = Order.objects.create(user=request.user)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)

                try:
                    coupon = Coupon.objects.get(code=code)
                except ObjectDoesNotExist:
                    messages.info(self.request, "This coupon does not exist")
                    order.coupon = None
                    order.save()
                    return redirect("core:checkout")

                order.coupon = coupon
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")
