from django.contrib import admin
from .models import Contact, Product,User,Whishlist,Cart,Billing_Detail

# Register your models here.
admin.site.register(Contact)
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Whishlist)
admin.site.register(Cart)
admin.site.register(Billing_Detail)