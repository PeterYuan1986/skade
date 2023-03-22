from django.urls import path
from .views import *

app_name = 'core'

urlpatterns = [
    path('shop/', shop, name='shop'),
    path('shop/<slug:category>/', shop),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('order-history/', OrderHistoryView.as_view(), name='order-history'),
    path('product/<slug>/', item_detail, name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('checkout/<slug>/', buy_now, name='buy-now'),
    path('add-coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('request-refund/', RequestRefundView.as_view(), name='request-refund'),
    path('order-success/', order_success, name='order-success'),
    path('order-failed/', order_failed, name='order-failed'),
]
