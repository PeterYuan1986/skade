from django.contrib import admin

from .models import *


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user',
                    'admin_orderitems',
                    'ordered',
                    'being_delivered',
                    'received',
                    'refund_requested',
                    'refund_granted',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'coupon',
                    'checkout_session',
                    'ordered_date',
                    'full_address'
                    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = ['ordered',
                   'being_delivered',
                   'received',
                   'refund_requested',
                   'refund_granted']
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = ['id',
        'user',
        'street_address',
        'apartment_address',
        'city',
        'state',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type', 'state']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'body', 'stars', 'item', 'created_on', 'active')
    list_filter = ('active', 'created_on')
    search_fields = ('name', 'email', 'body')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('sku',)}


admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
