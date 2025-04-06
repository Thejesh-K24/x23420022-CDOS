from itertools import product
from unicodedata import name
from django.urls import path
from django.views import View
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('contact/',views.contact,name='contact'), 
    path('about/',views.about,name='about'),
    path('shop/',views.shop,name='shop'),
    path('cart/',views.cart,name='cart'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('logout/',views.logout,name='logout'),
    path('changepassword/',views.changepassword,name='changepassword'),
    path('sellerindex/',views.sellerindex,name='sellerindex'),
    path('add_product/',views.add_product,name='add_product'),
    path('view_product/',views.view_product,name='view_product'),
    path('seller_edit_product/<int:pk>/',views.seller_edit_product,name='seller_edit_product'),
    path('seller_delete_product/<int:pk>/',views.seller_delete_product,name='seller_delete_product'),
    path('collection_vegetables/',views.collection_vegetables,name='collection_vegetables'),
    path('collection_fruits/',views.collection_fruits,name='collection_fruits'),
    path('collection_juice/',views.collection_juice,name='collection_juice'),
    path('collection_dried/',views.collection_dried,name='collection_dried'),
    path('product_details/<int:pk>/',views.product_details,name='product_details'),
    path('add_to_whishlist/<int:pk>/',views.add_to_whishlist,name='add_to_whishlist'),
    path('remove_from_whishlist/<int:pk>/',views.remove_from_whishlist,name='remove_from_whishlist'),
    path('add_to_cart/<int:pk>/',views.add_to_cart,name='add_to_cart'),
    path('whishlist/',views.whishlist,name='whishlist'),
    path('remove_from_cart/<int:pk>/',views.remove_from_cart,name='remove_from_cart'),
    path('change_qty/',views.change_qty,name='change_qty'),
    path('pay/', views.initiate_payment, name='pay'),
    path('callback/', views.callback, name='callback'),
    path('myorders/', views.myorders, name='myorders'),
    path('ajax/validate_email/',views.validate_signup,name='validate_email'),
    path('buy_now/<int:pk>/',views.buy_now,name='buy_now'),
    path('buy_all_now/',views.buy_all_now,name='buy_all_now'),
]