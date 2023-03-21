import os
from django.db.models import Avg
from PIL import Image
from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField
from djecommerce.settings.base import BASE_DIR
from localflavor.us.models import USPostalCodeField, USZipCodeField

LABEL_CHOICES = (
    ('P', 'primary'),
    ('F', 'featured'),
    ('D', 'danger')
)
COLOR_CHOICES = (
    ('BLUE', 'BLUE'),
    ('BLACK', 'BLACK'),
    ('BEIGE', 'BEIGE'),
    ('RED', 'RED'),
    ('NONE', 'NONE'),
)
ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)
CONDITION_CHOSICES = (('NEW', 'NEW'), ('USED', 'USED'), ('REFURBISHED', 'REFURBISHED'))


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(default='no_img.jpg')

    # display = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Opening the uploaded image
        length = 500
        output_name = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'category_img'),
                                   self.slug + '.jpg')

        def crop(image, output, length):
            if image and image.name != 'no_img.jpg' and image != output:
                im = Image.open(image)
                if im.mode == "JPEG":
                    pass
                elif im.mode in ["RGBA", "P"]:
                    im = im.convert("RGB")
                im = im.resize((length, length), Image.ANTIALIAS)

                # after modifications, save it to the output
                im.save(output, format='JPEG', subsampling=0, quality=95)
                dst = os.path.join('category_img', self.slug + '.jpg')
                return dst
            else:
                return

        output = crop(self.image, output_name, length)
        self.image = output if output else 'no_img.jpg'
        super(Category, self).save()


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    color = models.CharField(choices=COLOR_CHOICES, max_length=5)
    sku = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)
    price_id = models.CharField(max_length=200)
    condition = models.CharField(choices=CONDITION_CHOSICES, max_length=11, default='NEW')
    description1 = models.CharField(max_length=254, blank=True, null=True)
    description2 = models.CharField(max_length=254, blank=True, null=True)
    description3 = models.CharField(max_length=254, blank=True, null=True)
    description4 = models.CharField(max_length=254, blank=True, null=True)
    description5 = models.CharField(max_length=254, blank=True, null=True)
    information = models.TextField(blank=True, null=True)
    brand = models.TextField(max_length=10,null=True,blank=True)
    image = models.ImageField(default='no_img.jpg')
    img1 = models.ImageField(default='no_img.jpg')
    img2 = models.ImageField(default='no_img.jpg')
    img3 = models.ImageField(default='no_img.jpg')
    img4 = models.ImageField(default='no_img.jpg')
    img5 = models.ImageField(default='no_img.jpg')

    a1 = models.ImageField(blank=True, null=True)
    a2 = models.ImageField(blank=True, null=True)
    a3 = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.slug

    def get_rating(self):
        stars_average = list(self.comments.filter(active=True).aggregate(Avg('stars')).values())[0]

        return stars_average if stars_average else 0

    def get_category_display(self):
        return

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def buy_now(self):
        return reverse("core:buy-now", kwargs={
            'slug': self.slug
        })

    def get_related_products(self):
        return Item.objects.filter(category=self.category)

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })

    def save(self, *args, **kwargs):
        # Opening the uploaded image
        length = 700
        a_length = 1000

        output_image = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                    self.slug + '_image.jpg')
        output_img1 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                   self.slug + '_img1.jpg')
        output_img2 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                   self.slug + '_img2.jpg')
        output_img3 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                   self.slug + '_img3.jpg')
        output_img4 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                   self.slug + '_img4.jpg')
        output_img5 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                   self.slug + '_img5.jpg')

        def crop(image, output, length):
            im = Image.open(image)
            if im.mode == "JPEG":
                pass
            elif im.mode in ["RGBA", "P"]:
                im = im.convert("RGB")
            im = im.resize((length, length), Image.ANTIALIAS)

            # after modifications, save it to the output
            im.save(output, format='JPEG', subsampling=0, quality=95)
            dst = os.path.join('listing_img', os.path.basename(output))
            return dst

        if self.image:
            self.image = crop(self.image, output_image, length)
        if self.img1:
            self.img1 = crop(self.img1, output_img1, length)
        if self.img2:
            self.img2 = crop(self.img2, output_img2, length)
        if self.img3:
            self.img3 = crop(self.img3, output_img3, length)
        if self.img4:
            self.img4 = crop(self.img4, output_img4, length)
        if self.img5:
            self.img5 = crop(self.img5, output_img5, length)

        def crop_a(image, output, a_length):
            im = Image.open(image)
            if im.mode == "JPEG":
                pass
            elif im.mode in ["RGBA", "P"]:
                im = im.convert("RGB")
            original_width, original_height = im.size
            aspect_ratio = round(a_length / original_width, 2)
            desired_width = a_length
            desired_height = round(original_height * aspect_ratio)
            im = im.resize((desired_width, desired_height), Image.ANTIALIAS)

            # after modifications, save it to the output
            im.save(output, format='JPEG', subsampling=0, quality=95)
            dst = os.path.join('listing_img', os.path.basename(output))
            return dst

        if self.a1:
            output_a1 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                     self.slug + '_a1.jpg')
            self.a1 = crop_a(self.a1, output_a1, a_length)
        if self.a2:
            output_a2 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                     self.slug + '_a2.jpg')
            self.a2 = crop_a(self.a2, output_a2, a_length)
        if self.a3:
            output_a3 = os.path.join(os.path.join(os.path.join(BASE_DIR, 'media_root'), 'listing_img'),
                                     self.slug + '_a3.jpg')
            self.a3 = crop_a(self.a3, output_a3, a_length)
        super(Item, self).save()


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item added to cart
    2. Adding a billing address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging etc.)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return round(total,2)


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = USPostalCodeField()
    zip = USZipCodeField()
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    coupon_id = models.CharField(max_length=20)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


class Comment(models.Model):
    stars = models.IntegerField(default=5)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
