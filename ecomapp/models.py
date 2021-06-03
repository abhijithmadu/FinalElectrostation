from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.deletion import CASCADE
from phone_field import PhoneField
from django.conf import settings
from django.urls import reverse
from django.db.models import Avg
from django.db.models import Count
from .utils import generate_ref_code
# Create your models here.

class UserData(AbstractUser):

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)



class Category(models.Model):
    name=models.CharField(max_length=100,null=True)
    slug= models.SlugField(unique=True)
    def get_url(self):
        return reverse('product_by_category',args=[self.slug]) 

    def __str__(self):
        return self.name

class Product(models.Model):
    name=models.CharField(max_length=100,null=True)
    slug=models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price=models.FloatField()   
    description = models.TextField()    
    stock = models.IntegerField() 
    image1=models.ImageField(upload_to="products")
    image2=models.ImageField(upload_to="products",default='')
    image3=models.ImageField(upload_to="products",default='')
    image4=models.ImageField(upload_to="products",default='')
    offer_price=models.FloatField(null=True)
    offer_percentage= models.FloatField(null=True)

    def product_price(self):
        if self.offer_price == None:
            return self.price 
        else:           
            return self.price - self.offer_price


   
    def get_url(self):
        return reverse('product_details',args=[self.slug])

    def __str__(self):
        return self.name
    
    def averageReview(self):
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        avg = 0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg    

    def countReview(self):
        reviews = ReviewRating.objects.filter(product=self,status=True).aggregate(count=Count('id'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count 


class VariationManager(models.Manager):
    def color(self):
        return super(VariationManager, self).filter(variation_category='color',is_active=True)
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size',is_active=True)

variation_category_choice=(
    ('color','color'),
    ('size','size'),
)

class Variation(models.Model):
    product =models.ForeignKey(Product, on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=100,choices=variation_category_choice)
    variation_value = models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now=True)
    objects = VariationManager()

    def __str__(self):
        return self.variation_value


class Cart(models.Model):
    cart_id = models.CharField(max_length=250,blank=True)
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user =models.ForeignKey(UserData, on_delete=models.CASCADE,null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart= models.ForeignKey(Cart, on_delete=models.CASCADE,null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    

    def sub_total(self):
        if self.product.offer_price == None:
            return self.product.price * self.quantity
        else:
            return (self.product.price - self.product.offer_price) * self.quantity


    def __unicode__(self):
        return self.product


class UserProfile(models.Model):
    user=models.OneToOneField(UserData,on_delete=models.CASCADE)
    address_line_1= models.CharField(blank=True,max_length=100)
    address_line_2= models.CharField(blank=True,max_length=100)
    profile_picture=models.ImageField(blank=True,upload_to="userprofile")
    city=models.CharField(blank=True,max_length=20)
    state=models.CharField(blank=True,max_length=20)
    country=models.CharField(blank=True,max_length=20)


    def __str__(self):
        return self.user.username


    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'


class ReviewRating(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    user = models.ForeignKey(UserData,on_delete=models.CASCADE)
    subject = models.CharField(max_length=100,blank=True)
    review = models.CharField(max_length=500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20,blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.subject

class Profile(models.Model):
    userprofile = models.OneToOneField(UserData, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    code = models.CharField(max_length=12, blank=True)
    recommented_by = models.ForeignKey(UserData, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.userprofile.username}~{self.code}"

    def get_recommented_profiles(self):
        pass
    def save(self, *args, **kwargs):
        if self.code == "":
            code = generate_ref_code()
            self.code = code
        super().save(*args, **kwargs)

        
class CategoryOffer(models.Model):
    category=models.OneToOneField(Category,on_delete=models.CASCADE)
    offer=models.IntegerField()
    offer_start=models.DateField()
    offer_end=models.DateField()

    
  

class ProductOffer(models.Model):
    product=models.OneToOneField(Product,on_delete=models.CASCADE)
    offer=models.IntegerField()
    offer_start=models.DateField()
    offer_end=models.DateField()

    
class ReferalCoupen(models.Model):
    user=models.ForeignKey(UserData,on_delete=models.CASCADE) 
    coupen_code=models.CharField(max_length=12,blank=True)
    discount=models.IntegerField(default=20)   


    def __str__(self):
        return self.coupen_code    
      

class SimpleCoupen(models.Model):
    coupen_title=models.CharField(max_length=30)  
    coupen_code=models.CharField(max_length=30)
    coupen_offer=models.FloatField()
    validity=models.BooleanField(default=True)

class UsedOffer(models.Model):
    user=models.ForeignKey(UserData,on_delete=models.CASCADE)
    coupen=models.ForeignKey(SimpleCoupen,on_delete=models.CASCADE)  


class Adminlogin(models.Model):
    username = models.CharField(max_length=10,null=True)
    password = models.CharField(max_length=20, null=True)   


