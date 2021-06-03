from django.urls import path
from . import views

urlpatterns = [
    path('place_order',views.place_order,name='place_order'),
    path('payments',views.payments,name='payments'),
    path('dashboard',views.dashboard,name='dashboard'),
    path('my_orders',views.my_orders,name='my_orders'),
    path('ordercomplete',views.ordercomplete,name='ordercomplete'),
    path('editprofile',views.editprofile,name='editprofile'),
    path('orderdetails',views.order_details,name='orderdetails'),
    path('orderproductdetails',views.order_product_details,name='orderproductdetails'),
    path('order_cancel/<int:id>/',views.order_cancel,name='order_cancel'),
    path('orderproductdetailsadmin/<int:id>/',views.orderproductdetails,name='orderproductdetailsadmin'),
    path('payoption',views.payoption,name='payoption'),
    path('razorpay',views.razorpay,name='razorpay'),
    path('address',views.user_address,name='address'),
    path('deladdress/<int:id>/',views.user_address_delete,name='deladdress'),
    path('editaddress/<int:id>/',views.user_edit_address,name='editaddress'),
    path('collectaddress',views.collect_address,name='collectaddress'),
    path('salesreport',views.monthly_sales,name='salesreport'),
    path('yearlyreport',views.yearly_sales,name='yearlyreport'),
    path('datewise',views.datewise_sales,name='datewise'),

]