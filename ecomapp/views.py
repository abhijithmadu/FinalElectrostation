from orders.models import UserAddress,OrderProduct,ProductOffer,CategoryOffer,ReferalCoupen
from re import L
import re
from typing import ContextManager
from django import http
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.shortcuts import render,get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.models import User,auth
from .models import Adminlogin, Product, Profile, ReviewRating, SimpleCoupen, UsedOffer,UserData,Category,Cart,CartItem,Variation
from .forms import Addproduct,Addcategory, Addvariation, ReviewForm, SimpleCouponForm
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.sessions.models import Session
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger,Paginator
from django.core.exceptions import ObjectDoesNotExist
import requests
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import os
from twilio.rest import Client
import random
from datetime import datetime
import uuid
from django.core.files.base import ContentFile
import base64


# Create your views here.

@never_cache       
@cache_control(max_age=0, no_cache=True, must_revalidate=True, no_store=True)
def index(request):
    categories = request.GET.get('categories')
    if categories == None:
        product = Product.objects.all()
    else:
        product = Product.objects.filter(category_name=categories)

    category=Category.objects.all()
    context={
        'product':product,
        'category':category,
    }
    return render(request,'index.html',context)

@cache_control(max_age=0,no_cache=True, must_revalidate=True, no_store=True)
def product_details(request,slug):

    product = Product.objects.get(slug = slug)

    reviews = ReviewRating.objects.filter(product_id=product.id,status=True)

    context={
        'product':product,
        'reviews':reviews,
    }
    return render(request,'product_detail.html',context)


@cache_control(max_age=0,no_cache=True, must_revalidate=True, no_store=True)
def variation_details(request):
    if request.session.has_key('is_logged'):
        
        variation = Variation.objects.all()
        return render(request,'variation_details.html',{'variation':variation})
    else:
        return redirect('admin_login')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_variation(request): 
    
    if request.session.has_key('is_logged'): 
         
    
        varform = Addvariation() 
        if request.method == 'POST':
            varform = Addvariation(request.POST)
            
            if varform.is_valid():

                product= varform.cleaned_data["product"]
                variation_category= varform.cleaned_data["variation_category"]
                variation_value= varform.cleaned_data["variation_value"]
                is_active=varform.cleaned_data["is_active"]
                var= Variation(product,variation_category,variation_value,is_active)
                varform.save()
                return redirect('variation_details')

        return render(request,'addvariation.html',{'varform':varform})
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_variation(request,id):
    if request.session.has_key('is_logged'):
   
        vat = Variation.objects.get(id=id)
        varform = Addvariation(instance=vat)
        if request.method == 'POST':

            varform = Addvariation(request.POST,request.FILES,instance=vat)
            
            if varform.is_valid():

                varform.save()
                return redirect('variation_details')

        context={'varform':varform}

        return render(request,'editvariation.html',context)
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def variation_delete(request,id):
    if request.session.has_key('is_logged'):

        variation = Variation.objects.get(id=id)
        variation.delete()

        # messages.error(request,"deleted successfully")
        return redirect("variation_details")
        # else:
        #     return redirect('admin_login')  
    else:
        return redirect('admin_login')  




@cache_control(max_age=0,no_cache=True, must_revalidate=True, no_store=True)
def category_details(request):
    if request.session.has_key('is_logged'):
        
        category = Category.objects.all()
        return render(request,'categorydetails.html',{'category':category})
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_category(request,slug):
    if request.session.has_key('is_logged'):
   
        cat = Category.objects.get(slug=slug)
        catform = Addcategory(instance=cat)
        if request.method == 'POST':

            catform = Addcategory(request.POST,request.FILES,instance=cat)
            
            if catform.is_valid():

                # product = Product(name,slug,category,image,price,description,stock)

                catform.save()
                return redirect('category_details')

        context={'catform':catform}

        return render(request,'edit_category.html',context)
    else:
        return redirect('admin_login')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_category_delete(request,id):
    if request.session.has_key('is_logged'):

        category = Category.objects.get(id=id)
        category.delete()

        # messages.error(request,"deleted successfully")
        return redirect("category_details")
        # else:
        #     return redirect('admin_login')  
    else:
        return redirect('admin_login')  

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    # addproduct = Addproduct
    if request.session.has_key('is_logged'):   
    
        form =Addproduct()
        if request.method == 'POST':
            form = Addproduct(request.POST,request.FILES)
            
            if form.is_valid():

                name= form.cleaned_data["name"]
                slug= form.cleaned_data["slug"]
                category= form.cleaned_data["category"]
               
                price= form.cleaned_data["price"]
                description = form.cleaned_data["description"]
                stock = form.cleaned_data["stock"]
                image1 = request.POST['pro_img1']
                image2 = request.POST['pro_img2']
                image3 = request.POST['pro_img3']
                image4 = request.POST['pro_img4']

                format, img1 = image1.split(';base64,')
                ext = format.split('/')[-1]
                img_data1 = ContentFile(base64.b64decode(img1), name=name + '1.' + ext)
                format, img2 = image2.split(';base64,')
                ext = format.split('/')[-1]
                img_data2 = ContentFile(base64.b64decode(img2), name=name + '2.' + ext)
                format, img3 = image3.split(';base64,')
                ext = format.split('/')[-1]
                img_data3 = ContentFile(base64.b64decode(img3), name=name + '3.' + ext)
                format, img4 = image4.split(';base64,')
                ext = format.split('/')[-1]
                img_data4 = ContentFile(base64.b64decode(img4), name=name + '4.' + ext)

                product = Product(name=name,slug=slug,category=category,price=price,description=description,stock=stock,image1=img_data1,image2=img_data2,image3=img_data3,image4=img_data4)

                product.save()
                return redirect('admin_product_details')

        return render(request,'addproduct.html',{'form':form})
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_category(request): 
    
    if request.session.has_key('is_logged'): 
         
    
        catform = Addcategory() 
        if request.method == 'POST':
            catform = Addcategory(request.POST)
            
            if catform.is_valid():

                name= catform.cleaned_data["name"]
                slug= catform.cleaned_data["slug"]

                cat = Category(name,slug)
                catform.save()
                return redirect('admin_panel')

        return render(request,'addcategory.html',{'catform':catform})
    else:
        return redirect('admin_login')

def add_coupon(request):
     if request.session.has_key('is_logged'):
         couponform = SimpleCouponForm()
         if request.method == 'POST':
             couponform = SimpleCouponForm(request.POST)

             if couponform.is_valid():
                 coupen_title = couponform.cleaned_data['coupen_title']
                 coupen_code =  couponform.cleaned_data['coupen_code']
                 coupen_offer =  couponform.cleaned_data['coupen_offer']

                 coupon = SimpleCoupen(coupen_title=coupen_title,coupen_code=coupen_code,coupen_offer=coupen_offer)

                 coupon.save()
                 return redirect('admin_panel')
                 
         return render(request,'addcoupon.html',{'couponform':couponform})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_coupon(request):

    if request.session.has_key('is_logged'):
        coupon = SimpleCoupen.objects.all()
        return render(request,'coupondetails.html',{'coupon':coupon})
    else:
        return redirect('admin_login')

def user_view_coupon(request):
    
    coupon = SimpleCoupen.objects.all()
    return render(request,'usercoupondetails.html',{'coupon':coupon})

        
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def coupon_delete(request,id):
    if request.session.has_key('is_logged'):

        coupon = SimpleCoupen.objects.get(id=id)
        coupon.delete()

        # messages.error(request,"deleted successfully")
        return redirect("view_coupon")
        # else:
        #     return redirect('admin_login')  
    else:
        return redirect('admin_login')  



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_product_details(request):
    if request.session.has_key('is_logged'):
        product = Product.objects.all()
        paginator=Paginator(product,4)
        page=request.GET.get('page')
        paged_product=paginator.get_page(page)
        return render(request,'admin_product_details.html',{'products':paged_product})
    else:
        return redirect('admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_product_delete(request,id):
    if request.session.has_key('is_logged'):

        product = Product.objects.get(id=id)
        product.delete()

        # messages.error(request,"deleted successfully")
        return redirect("admin_product_details")
        # else:
        #     return redirect('admin_login')  
    else:
        return redirect('admin_login')  
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_product(request,slug):
    if request.session.has_key('is_logged'):
   
        pro = Product.objects.get(slug=slug)
        form = Addproduct(instance=pro)
        if request.method == 'POST':

            form = Addproduct(request.POST,request.FILES,instance=pro)
            
            if form.is_valid():

                # product = Product(name,slug,category,image,price,description,stock)

                form.save()
                return redirect('admin_product_details')

        context={'form':form}

        return render(request,'editproduct.html',context)
    else:
        return redirect('admin_login')

def profile_view(request,ref_code):
    ref_id=str(ref_code)
    try:
        profile=Profile.objects.get(code=ref_id)
        request.session['ref_profile']=profile.id
        print(request.session['ref_profile'])
        print("try end")
    except:
        pass   


def generate_coupen():
    coupen=str(uuid.uuid4()).replace("-","")[:4]
    return coupen


def check_referal(request):
    if request.method == "GET":
        referal=request.GET['referal']
        if Profile.objects.filter(code=referal).exists():
            return HttpResponse("available")
        else:
            return HttpResponse("not available")            


def verify_coupen(request):
    if request.method=='POST':
        coupen=request.POST['coupen']
        if ReferalCoupen.objects.filter(coupen_code=coupen).exists():
            cartitem=CartItem.objects.filter(user=request.user)
            print(cartitem)
            for products in cartitem:
                if products.product.offer_price == None:
                    
                    price=products.product.price*(10/100)
                    products.product.offer_price=products.product.price-price
                    products.product.save()
                else:
                    price=products.product.offer_price*(10/100)  
                    products.product.offer_price=products.product.offer_price-price
                    products.product.save()
                   
            ref=ReferalCoupen.objects.get(coupen_code = coupen)
            ref.delete()
            messages.success(request,'your reference coupen is applied')
            return redirect('checkout')
        elif SimpleCoupen.objects.filter(coupen_code=coupen).exists():
            coupen_obj=SimpleCoupen.objects.get(coupen_code=coupen)
            if UsedOffer.objects.filter(coupen=coupen_obj,user=request.user).exists():
                messages.error(request,'you already used this coupen')  
                return redirect('checkout') 
            else:
                coupen_obj=SimpleCoupen.objects.get(coupen_code=coupen)
                cartitem=CartItem.objects.filter(user=request.user)
                for pro in cartitem:
                    if pro.product.offer_price == None:
                        
                        price=pro.product.price*(int(coupen_obj.coupen_offer)/100)
                        pro.product.offer_price=pro.product.price-price
                        pro.product.save()
                    else:
                        price=pro.product.offer_price*(int(coupen_obj.coupen_offer)/100)  
                        pro.product.offer_price=pro.product.offer_price-price
                        pro.product.save()
                used_offer=UsedOffer(coupen=coupen_obj,user=request.user)
                used_offer.save()
                messages.success(request,'your coupen is applied')
                return redirect('checkout') 
        else:
            messages.error(request,'coupen is invalid ')
            return redirect('checkout')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_registration(request, *args, **kwargs):
    if request.user.is_authenticated:
        return redirect('index')
    else:
        if request.method == 'POST':
            
            username=request.POST['username']
            email=request.POST['email']
            phone=request.POST['phone']
            password=request.POST['password1']
            confirm_password= request.POST['password2']
            ref_code=request.POST['referal']
            if password !=confirm_password:
                return render(request, 'user_register.html',{'error': "Password is not matched"})
            elif(UserData.objects.filter(username=username)).exists() or (UserData.objects.filter(email=email)).exists():
                return render(request,'user_register.html',{'error': "This User already avialable"})
            
            else:
                user = UserData.objects.create_user(username=username,email=email,phone=phone,password=password)
                profile_view(request,ref_code)
                referal_id=request.session.get('ref_profile')

                if referal_id is not None:
                    recommended_by_profile=Profile.objects.get(id=referal_id)
                    registered_user=UserData.objects.get(id=user.id)
                    # print(registered_user)
                    registered_profile=Profile.objects.get(userprofile=registered_user)
                    # print(registered_profile)
                    registered_profile.recommented_by = recommended_by_profile.userprofile
                    # print(registered_profile.recommented_by)
                    registered_profile.save()
                    # del request.session['ref_profile']
                    if registered_profile.recommented_by == None:
                        pass
                    else:
                        generate=generate_coupen()
                        coupen="REF"+generate
                        coupen=ReferalCoupen(user=user,coupen_code=coupen)
                        coupen.save()



                return redirect('index')
        else:
            return render(request, 'user_register.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_details(request):

    if request.session.has_key('is_logged'):
        # userdetail = UserData.objects.all()
        userdetail = UserData.objects.exclude(is_superuser=1)

        return render(request,'user_details.html',{'userdetail':userdetail})
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_delete(request,id):
    if request.session.has_key('is_logged'):
        userdelete = UserData.objects.get(id=id)
        userdelete.delete()

        # messages.error(request,"deleted successfully")
        return redirect("user_details")
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_panel(request):
    
    
    if request.session.has_key('is_logged'):
        order= OrderProduct.objects.all()
        new_users = UserData.objects.filter(date_joined__month=datetime.now().month).count()
        today_order=OrderProduct.objects.filter(created_at__day=datetime.now().day).count()
        day1=datetime.now().day
        day2=day1-1
        day3=day2-1
        day4=day3-1
        day5=day4-1
        day6=day5-1
        day7=day6-1

        day1_order =OrderProduct.objects.filter(created_at__day=day1).count()
        day2_order =OrderProduct.objects.filter(created_at__day=day2).count()
        day3_order =OrderProduct.objects.filter(created_at__day=day3).count()
        day4_order =OrderProduct.objects.filter(created_at__day=day4).count()
        day5_order =OrderProduct.objects.filter(created_at__day=day5).count()
        day6_order =OrderProduct.objects.filter(created_at__day=day6).count()
        day7_order =OrderProduct.objects.filter(created_at__day=day7).count()
        context={
            'new_user':new_users,
            'new_order':today_order,
            'order':order,
            'day1':day1_order,'day2':day2_order,'day3':day3_order,'day4':day4_order,'day5':day5_order,'day6':day6_order,'day7':day7_order

        }
        return render(request,'admindash.html',context)
    else:
        return redirect('admin_login')
    
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_block(request,id):
    if request.session.has_key('is_logged'):
        user=UserData.objects.get(id=id)
        user.is_active=False
        user.save()
        return redirect('user_details')
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_unblock(request,id):
    if request.session.has_key('is_logged'):
        user=UserData.objects.get(id=id)
        user.is_active=True
        user.save()
        return redirect(user_details)
    else:
        return redirect('admin_login')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_login(request):
    if request.session.has_key('is_logged'):
        return redirect('admin_panel')

    elif request.method =='POST':
        # uname="admin@gin.com"
        # pwd="admin"
        user=Adminlogin.objects.get(id=1)
        print(user.username,user.password)


        username=request.POST['username']
        password=request.POST['password']

        if username == user.username and password == user.password:
        # if UserData.objects.filter(username=username,password=password).exists():

            request.session['is_logged']=True
            return redirect('admin_panel')
        else:
            messages.error(request,'Invalid username or password')
            return redirect('admin_login')
    else:
        return render(request,'admin_login.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def admin_logout(request):
    del request.session['is_logged']
    return redirect('admin_login')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def user_login(request):
    if request.user.is_authenticated:
        return redirect('index')

    elif request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user is not None:
            try:
                
                cart=Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:
                    cart_item=CartItem.objects.filter(cart=cart)

                    product_variation=[]
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    # get the cart items from the user to access his product variation

                    cart_item = CartItem.objects.filter(user= user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)


                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity +=1
                            item.user=user
                            item.save()
                        else:
                            cart_item=CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user=user
                                item.save()                  

             
            except:                
                pass

            login(request,user)
            request.session['logged']=True
            url = request.META.get('HTTP_REFERER')
            try:
                query= requests.utils.urlparse(url).query
                params=dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('index')
                    
        else:
            messages.error(request,'Invalid username or password')
            return render(request,'user_login.html')    

    else:
        return render(request,'user_login.html')
    
@cache_control(max_age=0,no_cache=True, must_revalidate=True, no_store=True)
def user_logout(request):
    auth.logout(request)
    request.session['is_logged']= True
    return redirect('index')


def store(request,category_slug=None):
    categories = None
    product = None


    if category_slug != None:
        categories = get_object_or_404(Category,slug=category_slug)
        product=Product.objects.filter(category=categories)
        paginator= Paginator(product, 6)
        page= request.GET.get('page')
        page_products =  paginator.get_page(page)
        product_count=product.count()
    else:    
        product = Product.objects.all()
        paginator= Paginator(product, 6)
        page= request.GET.get('page')
        page_products =  paginator.get_page(page)
        product_count=product.count()
    context ={
        'product': page_products,
        'product_count':product_count,

    }
    return render(request, 'store.html',context)


def _cart_id(request):
    cart= request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request,product_id):
    current_user=request.user
    product= Product.objects.get(id=product_id)
    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method =='POST':
            for item in request.POST:

                key=item
                value = request.POST[key]

                try:
                    variation= Variation.objects.get(product=product ,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
            
        
        is_cart_item_exists = CartItem.objects.filter(product=product,user=current_user).exists()

        if is_cart_item_exists:

            cart_item = CartItem.objects.filter(product=product,user=current_user)
            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id=id[index]
                item = CartItem.objects.get(product=product, id= item_id)
                item.quantity +=1
                item.save()
            else:
                item =CartItem.objects.create(product=product,quantity=1,user=current_user)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

            # cart_item.quantity +=1 #cart_ite.quantity= cart_ite.quantity+1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity=1,
                user=current_user,

            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()
        return redirect('cart')

    # the user is not authenticated
    else:  
        product_variation = []
        if request.method =='POST':
            for item in request.POST:

                key=item
                value = request.POST[key]

                try:
                    variation= Variation.objects.get(product=product ,variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except:
                    pass
            
        
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))# get the cart using the cart id present in the session
        except Cart.DoesNotExist:
            cart=Cart.objects.create(
                cart_id=_cart_id(request)

            )
        cart.save()
        is_cart_item_exists = CartItem.objects.filter(product=product,cart=cart).exists()

        if is_cart_item_exists:

            cart_item = CartItem.objects.filter(product=product,cart=cart)
            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id=id[index]
                item = CartItem.objects.get(product=product, id= item_id)
                item.quantity +=1
                item.save()
            else:
                item =CartItem.objects.create(product=product,quantity=1,cart=cart)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)

            # cart_item.quantity +=1 #cart_ite.quantity= cart_ite.quantity+1
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity=1,
                cart=cart,

            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)

            cart_item.save()
        return redirect('cart')
        
def remove_cart(request,product_id,cart_item_id):
    
    product =get_object_or_404(Product,id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item =CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else:
            cart= Cart.objects.get(cart_id=_cart_id(request))
            cart_item =CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request,product_id,cart_item_id):
    
    product =get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated:
        cart_item =CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
    else:
        cart= Cart.objects.get(cart_id=_cart_id(request))
        cart_item =CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def cart(request,total=0,quantity=0,cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart= Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            if cart_item.product.offer_price == None:
                total += (cart_item.product.price * cart_item.quantity)
            else:
                total += (cart_item.product.price - cart_item.product.offer_price) * cart_item.quantity
            quantity += cart_item.quantity
            tax = (2*total)/100
            grand_total= tax+total
    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }

    return render(request, 'cart.html',context)



@login_required(login_url='user_login')
def checkout(request,total=0,quantity=0,cart_items=None):
    
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
                cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else:
            cart= Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity+=cart_item.quantity
        tax= (2*total)/100
        grand_total=total+tax
    except ObjectDoesNotExist:
        pass
    addresses = UserAddress.objects.filter(user=request.user)
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,
        'addresses':addresses
    }
    return render(request,'checkout.html',context)



def search(request):
    if 'keyword' in request.GET:
        keyword=request.GET.get('keyword')
        if keyword:
            products=Product.objects.filter(Q(name__icontains=keyword))
    context={
        'product':products,

    }

    return render(request,'store.html',context)  



def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if UserData.objects.filter(email=email).exists():
            user = UserData.objects.get(email__exact = email)
            current_site = get_current_site(request)
            mail_subject ='Reset Your Password'
            message = render_to_string('reset_password_email.html',{
                'user':user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),

            })
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()
            # message.success(request,'Password reset email has been  send to your email address')
            return redirect('user_login')
        else:
            messages.error(request,'Account Does not exist')
            return redirect('forgotpass')

    return render(request,'forgotpass.html')
    
def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserData._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError, UserData.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token) :

        request.session['uid'] = uid
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link has been expired')
        return redirect('user_login')


def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            uid = request.session.get('uid')
            user = UserData.objects.get(pk=uid)
            user.set_password(password)
            messages.success(request,'password reset successful')
            return redirect('user_login')
        else:
            messages.error(request,'Password not match')
            return redirect('resetpassword')
    else:
        return render(request,'resetpassword.html')



def otp_login(request):
    if request.method == 'POST':
        phone =  request.POST['phone']
        if UserData.objects.filter(phone=phone).exists():
            otp = random.randint(100000,999999)
            strotp=str(otp)
            account_sid ='AC575efb983ed0da194d2974bebbffe58d'
            auth_token ='84fb245c841a56166cbf705bf985c338'
            client = Client(account_sid, auth_token)
            message = client.messages \
                .create(
                     body="your otp is"+strotp,
                     from_='+16196484531',
                     to='+91'+phone
                 )
            request.session['otp']=otp
            print(request.session['otp'])
            request.session['phone']=phone
            print(request.session['phone'])
            print(otp,phone)
            messages.success(request,"OTP Sended Successfully")
            return redirect('otpverify')  
        else:
            messages.error(request,"enter a valid phone number")    
            return redirect('login')

    return render(request,'login.html')  
    
  

def otp(request):
    if request.method == 'POST':
        enter_otp=request.POST['otp']
        otp=int(enter_otp)
        print(type(otp))
        if request.session.has_key('otp'):
            sended_otp=request.session['otp']
            print(type(sended_otp))
            if sended_otp == otp :
                phone=request.session['phone']
                user=UserData.objects.get(phone=phone)
                login(request,user)
                del request.session['otp']
                del request.session['phone']

                return redirect('index')
            else:    
                messages.error(request,"entered OTP is wrong")
                return redirect('mobilelogin') 

    return render(request,'otplogin.html')



def submit_review(request,product_id): 

    url=request.META.get('HTTP_REFERER')    
    if request.method == 'POST':
        try:
            review=ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form=ReviewForm(request.POST,instance=review)
            form.save()
            # messages.success(request,'Your Review has been updated')
            return redirect(url)

        except ReviewRating.DoesNotExist:
            form=ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.rating=form.cleaned_data['rating']
                data.review=form.cleaned_data['review']
                data.ip=request.META.get('REMOTE_ADDR')
                data.product_id=product_id
                data.user_id=request.user.id
                data.save()
                # messages.success(request,'Your Review has been submitted')
                return redirect(url)


def category_offer(request):
    if request.method=='POST':
        cat=request.POST['category']
        offer=request.POST['offer']
        start=request.POST['start']
        end=request.POST['end']
        category=Category.objects.get(id=cat)
        if CategoryOffer.objects.filter(category__name=category).exists():
            cats=CategoryOffer.objects.get(category=category)
            cats.category=category
            cats.offer=offer
            cats.offer_start=start
            cats.offer_end=end
            cats.save()
            print("saved")
        else:    
            category=CategoryOffer(category=category,offer=offer,offer_start=start,offer_end=end) 
            category.save()

        product=Product.objects.filter(category=category.id)
        for pro in product:
            pro.offer_price=(pro.price/100)*int(offer)
            pro.offer_percentage=offer        
            pro.save(update_fields=['offer_price','offer_percentage'])
             
        return redirect('admin_panel')
    else:
        category = Category.objects.all()
    context={

        'category':category,

    }
    return render(request,'categoryoffer.html',context)

def product_offer(request):
    if request.method == 'POST':
        prod=int(request.POST['product'])
        offer=request.POST['offer']
        start=request.POST['start']
        end=request.POST['end']
        print(prod,offer,start,end)
        product=Product.objects.get(id=prod)
        print(product)
        
        if ProductOffer.objects.filter(product__id=prod).exists():
            pro=ProductOffer.objects.get(product=prod)
            print(pro)
            pro.product=product
            pro.offer=offer
            pro.offer_start=start
            pro.offer_end=end
            pro.save()
            print("saved")
    
        else: 
            product=ProductOffer(product=product,offer=offer,offer_start=start,offer_end=end)   
            product.save()
        

        prod=Product.objects.get(id=prod) 
        print(prod)
        prod.offer_price=(prod.price/100)*int(offer)
        prod.offer_percentage=offer 
        prod.save()
        return redirect('admin_panel')
    else:
        product = Product.objects.all()
    context={

        'product':product,

    }

    return render(request,'productoffer.html',context)


def view_product_offer(request):
    product_offer=ProductOffer.objects.all()
    
    context={
        'pro_off':product_offer,
        
    }
    return render(request,'adminviewproductoffer.html',context)  

def view_category_offer(request):
  
    category_offer=CategoryOffer.objects.all()
    context={
        
        'cat_off':category_offer
    }
    return render(request,'adminviewoffer.html',context)  


def delete_pro_offer(request,id):
    offer=ProductOffer.objects.get(id=id)
    print(offer)
    pro=Product.objects.get(name=offer.product)
    print(pro)
    pro.offer_price=None
    pro.offer_percentage=None
    pro.save()
    offer.delete()  
    return redirect('view_product_offer') 


def delete_cat_offer(request,id):
    offer=CategoryOffer.objects.get(id=id)
    print(offer)
    pro=Product.objects.filter(category=offer.category)
    for pro in pro:
        pro.offer_price=None
        pro.offer_percentage=None
        pro.save(update_fields=['offer_price','offer_percentage'])
    offer.delete()    
        
    return redirect('view_category_offer')






        



 



        





