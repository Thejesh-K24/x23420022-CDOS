from email import message, utils
from email.policy import default
from http.client import UNSUPPORTED_MEDIA_TYPE
from itertools import product
from random import choices
from time import timezone
from unicodedata import name
from django.db import models
from django.forms import CharField
from django.utils import timezone

# Create your models here.
class Contact(models.Model):
    name=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    mobile=models.CharField(max_length=100)
    message=models.TextField()

    def __str__(self):
        return self.name

class User(models.Model):
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    mobile=models.CharField(max_length=100)
    address=models.TextField()
    password=models.CharField(max_length=100)
    usertype=models.CharField(max_length=100,default="user")

    def __str__(self):
        return self.fname

class Product(models.Model):
    CHOICE1=(
        ('vegetables','vegetables'),
        ('fruits','fruits'),
        ('juice','juice'),
        ('dried','dried'),
    )

    product_seller=models.ForeignKey(User,on_delete=models.CASCADE)
    product_collection=models.CharField(max_length=100,choices=CHOICE1)
    product_name=models.CharField(max_length=100)
    product_weight=models.CharField(max_length=100)
    product_price=models.CharField(max_length=100)
    product_desc=models.TextField()
    product_image=models.ImageField(upload_to="product_image/")

    def __str__(self):
        return self.product_seller.fname+" - "+self.product_collection+" - "+self.product_name

class Whishlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.fname+" - "+self.product.product_collection

class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    date=models.DateTimeField(default=timezone.now)
    product_price=models.PositiveBigIntegerField()
    product_qty=models.PositiveBigIntegerField()
    total_price=models.PositiveBigIntegerField()
    payment_status=models.CharField(max_length=100,default="pending")

    def __str__(self):
        return self.user.fname+" - "+self.product.product_collection

class Transaction(models.Model):
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)

class Billing_Detail(models.Model):
    CHOICE1=(
        ('gujarat','gujarat'),
        ('panjab','panjab'),
        ('rajasthan','rajasthan'),
        ('kerala','kerala'),
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE,default="1")
    fname=models.CharField(max_length=100)
    lname=models.CharField(max_length=100)
    state_country=models.CharField(max_length=100,choices=CHOICE1)
    street_address1=models.TextField()
    street_address2=models.TextField()
    city=models.CharField(max_length=100)
    postcode=models.CharField(max_length=100)
    mobile=models.CharField(max_length=100)
    email=models.CharField(max_length=100)

    def __str__(self):
        return self.user.fname