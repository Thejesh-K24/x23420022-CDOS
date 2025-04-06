from contextlib import redirect_stderr
from email import message
import email
from functools import total_ordering
from http.client import PAYMENT_REQUIRED
import imp
from itertools import product
from math import prod
from multiprocessing import reduction
import re
from unicodedata import name
from urllib import request
from django.shortcuts import render,redirect
from .models import Contact, Product, User, Whishlist, Cart, Transaction, Billing_Detail
from .paytm import generate_checksum, verify_checksum
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse

# Create your views here.

def initiate_payment(request):
    user=User.objects.get(email=request.session['email'])
    if request.method=="POST":
        Billing_Detail.objects.create(
            user=user,
            fname=request.POST['fname'],
            lname=request.POST['lname'],
            state_country=request.POST['state_country'],
            street_address1=request.POST['street_address1'],
            street_address2=request.POST['street_address2'],
            city=request.POST['city'],
            postcode=request.POST['postcode'],
            mobile=request.POST['mobile'],
            email=request.POST['email']
        )
        try:
            amount = int(request.POST['amount'])
        except:
            return render(request, 'pay.html', context={'error': 'Wrong Accound Details or amount'})

        transaction = Transaction.objects.create(made_by=user,amount=amount)
        transaction.save()
        merchant_key = settings.PAYTM_SECRET_KEY

        params = (
            ('MID', settings.PAYTM_MERCHANT_ID),
            ('ORDER_ID', str(transaction.order_id)),
            ('CUST_ID', str(transaction.made_by.email)),
            ('TXN_AMOUNT', str(transaction.amount)),
            ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
            ('WEBSITE', settings.PAYTM_WEBSITE),
            # ('EMAIL', request.user.email),
            # ('MOBILE_N0', '9911223388'),
            ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
            ('CALLBACK_URL', 'http://sunil07.pythonanywhere.com/callback/'),
            # ('PAYMENT_MODE_ONLY', 'NO'),
        )

        paytm_params = dict(params)
        checksum = generate_checksum(paytm_params, merchant_key)

        transaction.checksum = checksum
        transaction.save()
        carts=Cart.objects.filter(user=user)
        for i in carts:
            i.payment_status="paid"
            i.save()
        carts=Cart.objects.filter(user=user,payment_status="pending")
        request.session['cart_count']=len(carts)
        paytm_params['CHECKSUMHASH'] = checksum
        print('SENT: ', checksum)
        return render(request, 'redirect.html', context=paytm_params)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return render(request, 'callback.html', context=received_data)
        return render(request, 'callback.html', context=received_data)

def index(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=="user":
            return render(request,'index.html')
        else:
            return render(request,'seller_index.html')
    except:
        return render(request,'index.html')

#def organicfoods(request):
    #return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def contact(request):
    if request.method=="POST":
        Contact.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            mobile=request.POST['mobile'],
            message=request.POST['message'],
        )
        msg="Contact Saved Successfully"
        return render(request,'contact.html',{'msg':msg})

    else:
        return render(request,'contact.html')

def shop(request):
    products=Product.objects.all().order_by('-id')[:]
    whishlists=Whishlist.objects.filter()
    request.session['whishlist_count']=len(whishlists)
    return render(request,'shop.html',{'products':products})

def login(request):
    if request.method=="POST":
        try:
            user=User.objects.get(
                email=request.POST['email'],
                password=request.POST['password']
                )
            if user.usertype=="user":
                request.session['email']=user.email
                request.session['fname']=user.fname
                whishlists=Whishlist.objects.filter(user=user)
                request.session['whishlist_count']=len(whishlists)
                carts=Whishlist.objects.filter(user=user)
                request.session['whishlist_count']=len(carts)
                return render(request,'index.html')
            else:
                request.session['email']=user.email
                request.session['fname']=user.fname
                return render(request,'seller_index.html')
        except:
            msg="Email and Password does not matched"
            return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def signup(request):
    if request.method=="POST":
        try:
            User.objects.get(email=request.POST['email'])
            msg="Email is Already Registerd"
            return render(request,'signup.html',{'msg':msg})
        except:
            if request.POST['password']==request.POST['cpassword']:
                User.objects.create(
                    usertype=request.POST['usertype'],
                    fname=request.POST['fname'],
                    lname=request.POST['lname'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    address=request.POST['address'], 
                    password=request.POST['password'],
                )
                msg="User Signup Successfully"
                return render(request,'login.html',{'msg':msg})
            else:
                msg="Password and Confirm Password does not Matched"
                return render(request,'signup.html',{'msg':msg})
    else:
        return render(request,'signup.html')

def logout(request):
    try:
        del request.session['email']
        del request.session['fname']
        return render(request,'login.html')
    except:
        return render(request,'login.html')

def changepassword(request):
    user=User.objects.get(email=request.session['email'])
    if user.usertype=="user":
        if request.method=="POST":
            if user.password==request.POST['oldpassword']:
                if request.POST['newpassword']==request.POST['cnewpassword']:
                    user.password=request.POST['newpassword']
                    user.save()
                    msg="Password Change Sucessfully"
                    return render(request,'changepassword.html',{'msg':msg})
                else:
                    msg="New Password and Confirm New Password Dose not Matched"
                    return render(request,'changepassword.html',{'msg':msg})
            else:
                msg="Old Password is Incorrect"
                return render(request,'changepassword.html',{'msg':msg})
        else:
            return render(request,'changepassword.html')
    else:
        if request.method=="POST":
            if user.password==request.POST['oldpassword']:
                if request.POST['newpassword']==request.POST['cnewpassword']:
                    user.password=request.POST['newpassword']
                    user.save()
                    msg="Password Change Sucessfully"
                    return render(request,'seller_changepassword.html',{'msg':msg})
                else:
                    msg="New Password and Confirm New Password Dose not Matched"
                    return render(request,'seller_changepassword.html',{'msg':msg})
            else:
                msg="Old Password is Incorrect"
                return render(request,'seller_changepassword.html',{'msg':msg})
        else:
            return render(request,"seller_changepassword.html")

def sellerindex(request):
    return render(request,"seller_index.html")

def add_product(request):
    if request.method=='POST':
        product_seller=User.objects.get(email=request.session['email'])
        Product.objects.create(
            product_seller=product_seller,
            product_collection=request.POST['product_collection'],
            product_name=request.POST['product_name'],
            product_weight=request.POST['product_weight'],
            product_price=request.POST['product_price'],
            product_desc=request.POST['product_desc'],
            product_image=request.FILES['product_image']
            )
        msg="Product Added Successfully"
        return render(request,"add_product.html",{'msg':msg})
    else:       
        return render(request,"add_product.html")

def view_product(request):
    product_seller=User.objects.get(email=request.session['email'])
    products=Product.objects.filter(product_seller=product_seller).order_by('-id')[:]
    return render(request,"view_product.html",{'products':products})

def seller_edit_product(request,pk):
    product=Product.objects.get(pk=pk)
    if request.method=='POST':
        product.product_collection=request.POST['product_collection']
        product.product_name=request.POST['product_name']
        product.product_weight=request.POST['product_weight']
        product.product_price=request.POST['product_price']
        product.product_desc=request.POST['product_desc']
        try:
            product.product_image=request.FILES['product_image']
        except:
            pass
        product.save()
        return render(request,"seller_edit_product.html",{'product':product})
    else:
        return render(request,"seller_edit_product.html",{'product':product})

def seller_delete_product(request,pk):
    product=Product.objects.get(pk=pk)
    product.delete()
    return redirect('view_product')

def collection_vegetables(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=="user":
            products=Product.objects.filter(product_collection="vegetables")
            return render(request,'shop.html',{'products':products})
        else:
            products=Product.objects.filter(product_collection="vegetables")
            return render(request,'view_product.html',{'products':products})
    except:
        products=Product.objects.filter(product_collection="vegetables")
        return render(request,'shop.html',{'products':products})

def collection_fruits(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=="user":
            products=Product.objects.filter(product_collection="fruits")
            return render(request,'shop.html',{'products':products})
        else:
            products=Product.objects.filter(product_collection="fruits")
            return render(request,'view_product.html',{'products':products})
    except:
        products=Product.objects.filter(product_collection="fruits")
        return render(request,'shop.html',{'products':products})

def collection_juice(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=="user":
            products=Product.objects.filter(product_collection="juice")
            return render(request,'shop.html',{'products':products})
        else:
            products=Product.objects.filter(product_collection="juice")
            return render(request,'view_product.html',{'products':products})
    except:
        products=Product.objects.filter(product_collection="juice")
        return render(request,'shop.html',{'products':products})

def collection_dried(request):
    try:
        user=User.objects.get(email=request.session['email'])
        if user.usertype=="user":
            products=Product.objects.filter(product_collection="dried")
            return render(request,'shop.html',{'products':products})
        else:
            products=Product.objects.filter(product_collection="dried")
            return render(request,'view_product.html',{'products':products})
    except:
        products=Product.objects.filter(product_collection="dried")
        return render(request,'shop.html',{'products':products})

def product_details(request,pk):
    wishlist_flag=False
    cart_flag=False
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    try:
        Whishlist.objects.get(user=user,product=product)
        wishlist_flag=True
    except:
        pass
    try:
        Cart.objects.get(user=user,product=product,payment_status="pending")
        cart_flag=True
    except:
        pass
    return render(request,'product_details.html',{'product':product,'wishlist_flag':wishlist_flag,'cart_flag':cart_flag})

def add_to_whishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    try:
        Whishlist.objects.get(user=user,product=product)
        return redirect('whishlist')
    except:
        Whishlist.objects.create(
            user=user,
            product=product,
        )
        return redirect('shop')

def whishlist(request):
    user=User.objects.get(email=request.session['email'])
    whishlists=Whishlist.objects.filter(user=user).order_by('-id')[:]
    request.session['whishlist_count']=len(whishlists)
    return render(request,'whishlist.html',{'whishlists':whishlists})

def remove_from_whishlist(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    whishlist=Whishlist.objects.get(user=user,product=product)
    whishlist.delete()
    return redirect('whishlist')

def add_to_cart(request,pk):      
    user=User.objects.get(email=request.session['email'])
    product=Product.objects.get(pk=pk)
    try:
        Cart.objects.get(user=user,product=product,payment_status="pending")
        return redirect('cart')
    except:
        product=Product.objects.get(pk=pk)
        user=User.objects.get(email=request.session['email'])
        Cart.objects.create(
            user=user,
            product=product,
            product_price=product.product_price,
            product_qty=1,
            total_price=product.product_price,
        )
        return redirect('cart')

def cart(request):
    net_price=0
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status="pending").order_by('-id')[:]
    for i in carts:
        net_price=net_price+i.total_price

    request.session['cart_count']=len(carts)
    return render(request,'cart.html',{'carts':carts,'net_price':net_price})

def remove_from_cart(request,pk):
    product=Product.objects.get(pk=pk)
    user=User.objects.get(email=request.session['email'])
    cart=Cart.objects.get(user=user,product=product,payment_status="pending")
    cart.delete()
    return redirect('cart')

def change_qty(request):
    cart=Cart.objects.get(pk=request.POST['cid'])
    product_qty=int(request.POST['product_qty'])
    cart.product_qty=product_qty
    s=cart.product_price
    cart.total_price=product_qty*int(s)
    print(product_qty)
    cart.save()
    return redirect('cart')

def myorders(request):
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status="paid")
    return render(request,'myorders.html',{'carts':carts})

def validate_signup(request):
    email=request.GET.get('email')
    data={
        'is_taken':User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

def buy_now(request,pk):
    product=Product.objects.get(pk=pk)
    return render(request,'checkout.html',{'product':product})

def buy_all_now(request):
    net_price=0
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,payment_status="pending").order_by('-id')[:]
    for i in carts:
        net_price=net_price+i.total_price
    return render(request,'checkout.html',{'net_price':net_price})