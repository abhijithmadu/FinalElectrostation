from ecomapp.views import category_offer
from django.contrib import admin
from .models import *
from django.utils.html import format_html

class VariationAdmin(admin.ModelAdmin):

    list_display= ('product','variation_category','variation_value','is_active')
    list_editable=('is_active',)
    list_filter=('product','variation_category','variation_value','is_active')

class userProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description='Profile Picture'
    list_display=('thumbnail','user','city','state','country')
# Register your models here.
admin.site.register(UserData)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Variation,VariationAdmin)
admin.site.register(UserProfile,userProfileAdmin)
admin.site.register(ReviewRating)
admin.site.register(Profile)
admin.site.register(CategoryOffer)
admin.site.register(ProductOffer)
admin.site.register(ReferalCoupen)
admin.site.register(SimpleCoupen)
admin.site.register(UsedOffer)
admin.site.register(Adminlogin)








