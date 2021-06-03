from django import forms
from django.db.models import fields
from .models import *



class Addproduct(forms.ModelForm):
    
    class Meta:
        model = Product
        fields = ['name','slug','category','price','description','stock','image1','image2','image3','image4']
        
    def __init__(self,*args,**kwargs):
        super(Addproduct,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'
        
class Addcategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'

class Addvariation(forms.ModelForm):
    class Meta:
        model= Variation
        fields='__all__'

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields=['subject','review','rating']

        
class SimpleCouponForm(forms.ModelForm):
    class Meta:
        model = SimpleCoupen
        fields = '__all__'


