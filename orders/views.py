import base64
from django.core.files.base import ContentFile
from django.db.models.query import InstanceCheckMeta

from django.shortcuts import get_object_or_404, redirect, render
from ecomapp.models import *
from .forms import *
from .models import *
import datetime
from django.http import HttpResponse,JsonResponse
from django.contrib import messages
import json
# Create your views here.
def razorpay(request):
    order_id=val()
    print(order_id)
    order_data=Order.objects.get(user=request.user,is_ordered=False,order_number=order_id)
    cart_items=CartItem.objects.filter(user=request.user)
    grand_total=0
    tax=0
    total=0
    for cart_item in cart_items:
        if cart_item.product.offer_price == None:
            total+=(cart_item.product.price * cart_item.quantity) 
        else:
            total += (cart_item.product.price - cart_item.product.offer_price) * cart_item.quantity 
    tax = (2*total)/100
    grand_total= total+tax 
    payment=Payment(user=request.user,payment_id=order_id,payment_method="razorpay",amount_paid=grand_total,status="completed")
    payment.save()
    order_data.payment=payment
    order_data.is_ordered=True
    order_data.save()
    
    for item in cart_items:
        orderproduct=OrderProduct()
        orderproduct.order=order_data
        orderproduct.user=request.user
        orderproduct.payment=payment
        orderproduct.product=item.product
        orderproduct.quantity=item.quantity
        if item.product.offer_price == None:
                orderproduct.product_price=item.product.price
        else:
            orderproduct.product_price=item.product.offer_price
        orderproduct.ordered=True
        orderproduct.save()
        product=Product.objects.get(id=item.product_id)
            
        print(product)
        product.stock -= item.quantity
        product.save()

    CartItem.objects.filter(user=request.user).delete()    

    return redirect('ordercomplete')
    

def payments(request,total=0,quantity=0):
    
    order_id = val()
    
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=order_id)

    cart_items=CartItem.objects.filter(user=request.user)
    
    

    grand_total=0
    tax=0
    for cart_item in cart_items:
        if cart_item.product.offer_price == None:
            total+=(cart_item.product.price * cart_item.quantity) 
        else:
            total += (cart_item.product.price - cart_item.product.offer_price) * cart_item.quantity

    tax = (2*total)/100  
    grand_total= total+tax 


    if request.method == 'POST':
        pay=request.POST['payment']
        if pay == "cod":
            payment=Payment(user=request.user,payment_id=order_id,payment_method=pay,status="completed")
            payment.save()
            order.payment=payment
            order.is_ordered=True
            order.save()

            for item in cart_items:
                orderproduct=OrderProduct()
                orderproduct.order_id=order.id
                orderproduct.user_id=request.user.id
                orderproduct.payment=payment
                orderproduct.product_id=item.product.id
                orderproduct.quantity=item.quantity
                if item.product.offer_price == None:
                    orderproduct.product_price=item.product.price
                else:
                    orderproduct.product_price=item.product.offer_price
                orderproduct.ordered=True
                orderproduct.save()

                cart_item=CartItem.objects.get(id=item.id)
                product_variation=cart_item.variations.all()
                orderproduct=OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()


                # reduce the quantity

                product=Product.objects.get(id=item.product_id)
                
                print(product)
                product.stock -= item.quantity
                product.save()

            CartItem.objects.filter(user=request.user).delete() 

            return redirect('ordercomplete')           
            
        else:
            context={'grand_total':grand_total,'order_id':order_id}
            return render(request,'paymentoption.html',context)   
        

    context={
            'order':order,
            'cart_items':cart_items,
            'total':total,
            'tax':tax,
            'grand_total':grand_total,
            'order_id':order_id
        }
    return render(request,'payments.html',context)

def payoption(request):
    
    body=json.loads(request.body)
    print(body)
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])
    
    payment=Payment(user=request.user,payment_id=body['trans_ID'],payment_method=body['payment_method'],amount_paid=order.order_totel,status=body['status'])
    payment.save()
    order.payment=payment
    order.is_ordered=True
    order.save()
    cart_items=CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct=OrderProduct()
        orderproduct.order=order
        orderproduct.user=request.user
        orderproduct.payment=payment
        orderproduct.product=item.product
        orderproduct.quantity=item.quantity
        if item.product.offer_price == None:
            orderproduct.product_price=item.product.price
        else:
            orderproduct.product_price=item.product.price - item.product.offer_price
            
        orderproduct.ordered=True
        orderproduct.save()
        product=Product.objects.get(id=item.product_id)        
       
        product.stock -= item.quantity
        product.save()
    CartItem.objects.filter(user=request.user).delete()  

    data={
        'order_number':order.order_number,
        'transID':payment.payment_id
    }   

    return JsonResponse(data)
    
    


def ordercomplete(request):
    order_id=val()
    orders_data=Order.objects.get(order_number=order_id)
    
    order=OrderProduct.objects.filter(order=orders_data)

    print(order)
    print("check")
    context={'orders':order,'orders_data':orders_data}
    return render(request,'ordercomplete.html',context)    

   
def place_order(request,total=0,quantity=0):
    current_user=request.user

    cart_items= CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count <=0:
        return redirect('store')
    grand_total=0
    tax=0   
    for cart_item in cart_items:
        if cart_item.product.offer_price == None:
            total+=(cart_item.product.price * cart_item.quantity) 
        else:
            total += (cart_item.product.price - cart_item.product.offer_price) * cart_item.quantity 

    tax= (2*total)/100
    grand_total=total+tax

    if request.method=='POST':
        form= OrderForm(request.POST)
        if form.is_valid():
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.order_note=form.cleaned_data['order_note']
            data.order_totel=grand_total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()

            yr=int(datetime.date.today().strftime('%Y'))
            dt=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d= datetime.date(yr,mt,dt)
            current_date=d.strftime("%Y%d%m")
            order_number=current_date + str(data.id)
            data.order_number=order_number
            data.save()

            # order = Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            # context={
            #     'order':order,
            #     'cart_items':cart_items,
            #     'total':total,
            #     'tax':tax,
            #     'grand_total':grand_total
            # }
            request.session['order_id']=order_number
            global val
            def val():
                return order_number

            return redirect('payments')
        
        else:
            return HttpResponse("false")
        # else:
        #     return redirect('checkout')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count()
    userprofile=UserProfile.objects.get(user_id=request.user.id)

    context={
        'orders_count':orders_count,
        'userprofile':userprofile,
    }
    return render(request, 'dasboard.html',context)

def my_orders(request):
    # order=Order.objects.filter(user=request.user)
    orders = OrderProduct.objects.filter(user=request.user).order_by('-created_at')

    print(orders)
    context={
        'orders':orders

    }

    
    return render(request,'my_orders.html',context)


def editprofile(request):
    userprofile=get_object_or_404(UserProfile,user=request.user)
    if request.method=='POST':
        user_form=UserForm(request.POST,instance=request.user)
        profile_form=UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"Your profile has been updated")
            return redirect('editprofile')
    else:
        user_form=UserForm(instance= request.user)
        profile_form=UserProfileForm(instance=userprofile)
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile
    }
    return render(request,'editprofile.html',context)

def order_details(request):

    if request.session.has_key('is_logged'):
        order = Order.objects.all()
        return render(request,'orderdetails.html',{'order':order})
    else:
        return redirect('admin_login')



def order_product_details(request):
    if request.session.has_key('is_logged'):
        orderproduct = OrderProduct.objects.all()
        return render(request,'orderproductdetails.html',{'orderproduct':orderproduct})
    else:
        return redirect('admin_login')


def order_cancel(request,id):
    order=OrderProduct.objects.get(id=id)
    order.user_cancel=True
    order.status = 'Cancelled'
    order.save()
    pro=order.product.id
    product=Product.objects.get(id=pro)
    product.stock +=1
    product.save()
    return redirect('my_orders')

def orderproductdetails(request,id):
    order_detail=OrderProduct.objects.get(id=id)
    # order=Order.objects.get(order_number=id)
    if request.method== 'POST':
        status=request.POST['status']
        order_detail.status=status
        order_detail.save()
        return redirect('orderdetails')
    
    context={
        'order_detail':order_detail,
        

    }
    return render(request,'orderdetailsadmin.html',context)

def user_address(request):

    addresses=UserAddress.objects.filter(user=request.user)
    if request.method=='POST':
        data=request.POST
        first_name=data['first_name']
        last_name=data['last_name']
        phone=data['phone']
        email=data['email']
        address_line1=data['address_line1']
        address_line2=data['address_line2']
        city=data['city']
        state=data['state']
        country=data['country']
        address=UserAddress(user=request.user,first_name=first_name,last_name=last_name,phone=phone,email=email,address_line1=address_line1,address_line2=address_line2,city=city,state=state,country=country)
        address.save()
        return redirect('address')

    context={'addresses':addresses}
    return render(request,'useraddress.html',context)

def user_address_delete(request,id):

    useraddressdelete = UserAddress.objects.filter(user=request.user,id=id)
    useraddressdelete.delete()
    
    return redirect('address')

def user_edit_address(request,id):
    useraddressedit = UserAddress.objects.get(id=id)
    if request.method == 'POST':
        data=request.POST
        first_name=data['first_name']
        last_name=data['last_name']
        phone=data['phone']
        email=data['email']
        address_line1=data['address_line1']
        address_line2=data['address_line2']
        city=data['city']
        state=data['state']
        country=data['country']

        useraddressedit.first_name = first_name
        useraddressedit.last_name = last_name
        useraddressedit.phone = phone
        useraddressedit.email = email
        useraddressedit.address_line1 = address_line1
        useraddressedit.address_line2 = address_line2
        useraddressedit.city = city
        useraddressedit.state = state
        useraddressedit.country = country

        useraddressedit.save()

        return redirect("address")

    else:
        return render(request,"address_edit.html",{'useraddressedit':useraddressedit})


def collect_address(request):
    if request.method == "GET":
        id=request.GET['address']
        print(id)
        add=UserAddress.objects.get(id=id)
        print(add.last_name)

        data = {}
        data['first_name']=add.first_name
        data['last_name']=add.last_name
        data['phone']=add.phone
        data['email']=add.email
        data['address1']=add.address_line1
        data['address2']=add.address_line2
        data['city']=add.city
        data['state']=add.state
        data['country']=add.country

        return HttpResponse(json.dumps(data), content_type="application/json")
    


def monthly_sales(request):
    if request.method == 'POST':
        month = request.POST['month']
        x=[]
        x = month.split("-")
        mon=int(x[1])
        deliver=OrderProduct.objects.filter(status='Delivered',created_at__month=mon)
        total=0
        for delive in deliver:
            total+=delive.product_price
        context={
            'ordered':deliver,
            'total':total
        }
        
        return render(request,'salesreport.html',context)
    totalorder=OrderProduct.objects.filter(status='Delivered') 
    total=0 
    for delive in totalorder:
            total+=delive.product_price
    context={
            'ordered':totalorder,
             'total':total
        }
         
    return render(request,'salesreport.html',context)  

def yearly_sales(request):
    if request.method=='GET':
        year=request.GET['year']
        totalorder=OrderProduct.objects.filter(created_at__year=year,status='Delivered')
        total=0
        for delive in totalorder:
            total+=delive.product_price
        context={
            'ordered':totalorder,
             'total':total
        }
        return render(request,'salesreport.html',context)     

def datewise_sales(request):
    if request.method=="GET":
        start=request.GET['start']           
        end=request.GET['end']   
        totalorder=OrderProduct.objects.filter(created_at__range=[start,end],status='Delivered')
        print(totalorder)
        print(start,end) 
        total=0
        for delive in totalorder:
            total+=delive.product_price
        context={
            'ordered':totalorder,
             'total':total
        }

        return render(request,'salesreport.html',context) 





    

        
        
    