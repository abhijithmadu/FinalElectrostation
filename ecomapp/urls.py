from django.urls import path
from ecomapp import views
from .views import *

urlpatterns = [
    
    path('',views.index,name='index'),
    #  product details
    path('product_details/<slug:slug>/',views.product_details,name='product_details'),
    path('admin/add_product',views.add_product,name='admin/add_product'),
    path('admin_product_details',views.admin_product_details,name='admin_product_details'),
    path('admin_product_delete/<int:id>/',views.admin_product_delete,name='admin_product_delete'),
    path('edit_product/<slug:slug>/',views.edit_product,name='edit_product'),
     path('add_category',views.add_category,name='add_category'),
    # user registration and login
    path('user_registration',views.user_registration,name='user_registration'),
     path('user_login',views.user_login,name='user_login'),
    path('user_logout',views.user_logout,name="user_logout"),
    # Admin user view details
    path('user_details',views.user_details,name='user_details'),
    path('user_delete/<int:id>/',views.user_delete,name='user_delete'),
    path('user_block/<int:id>/',views.user_block,name='user_block'),
    path('user_unblock/<int:id>/',views.user_unblock,name='user_unblock'),
    # admin login details
    path('admin_panel',views.admin_panel,name='admin_panel'),
    path('admin_login',views.admin_login,name='admin_login'),
    path('admin_logout',views.admin_logout,name='admin_logout'),
    # product store details
    path('store',views.store,name="store"),
    path('store/<slug:category_slug>/',views.store,name="product_by_category"),
    # cart details
    path('cart',views.cart,name="cart"),
    path('add_cart/<int:product_id>/',views.add_cart,name="add_cart"),
    path('submit_review/<int:product_id>/', views.submit_review, name="submit_review"),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/',views.remove_cart,name="remove_cart"),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/',views.remove_cart_item,name="remove_cart_item"),

    # referal url
    path('check_referal',views.check_referal,name='check_referal'),
    path('verify_coupen',views.verify_coupen,name='verify_coupen'),

    # checkout
    path('checkout',views.checkout,name='checkout'),
    path('category_details',views.category_details,name='category_details'),
    path('admin_category_delete/<int:id>/',views.admin_category_delete,name='admin_category_delete'),
    path('edit_category/<slug:slug>/',views.edit_category,name='edit_category'),

    #variation
    path('variation_details',views.variation_details,name='variation_details'),
    path('add_variation',views.add_variation,name='add_variation'),
    path('edit_variation/<int:id>/',views.edit_variation,name='edit_variation'),
    path('variation_delete/<int:id>/',views.variation_delete,name='variation_delete'),
    path('search',views.search,name='search'),

    # forgot password
    path('forgotpass',views.forgotpassword,name='forgotpass'),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'),
    path('resetpassword',views.resetpassword,name='resetpassword'),

    # login with otp
    path('mobilelogin',views.otp_login,name='mobilelogin'),
    path('otpverify',views.otp,name='otpverify'),

 
    # admin Offer

    path('view_product_offer',views.view_product_offer,name='view_product_offer'), 
    path('view_category_offer',views.view_category_offer,name='view_category_offer'), 
    path('delete_pro_offer/<int:id>/',views.delete_pro_offer,name='delete_pro_offer'), 
    path('delete_cat_offer/<int:id>/',views.delete_cat_offer,name='delete_cat_offer'), 
    path('category_offer',views.category_offer,name='category_offer'),
    path('product_offer',views.product_offer,name='product_offer'), 

    # coupon 
    path('addcoupon',views.add_coupon,name="addcoupon"),
    path('view_coupon',views.view_coupon,name="view_coupon"),
    path('user_view_coupon',views.user_view_coupon,name="user_view_coupon"),
    path('coupon_delete/<int:id>/',views.coupon_delete,name="coupon_delete"),

       
    
    

]