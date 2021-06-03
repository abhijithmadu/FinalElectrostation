from django import forms
from django.db.models import fields
from .models import *
from ecomapp.models import *


class OrderForm(forms.ModelForm):
    class Meta:
        model=Order
        fields=['first_name','last_name','phone','email','address_line_1','address_line_2','country','state','city','order_note']

class UserForm(forms.ModelForm):
    class Meta:
        model=UserData
        fields={'first_name','last_name','phone'}
    def __init__(self,*args,**kwargs):
        super(UserForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture=forms.ImageField(required=False, error_messages = {'invalid':{"image files only"}},widget=forms.FileInput)
    class Meta:
        model=UserProfile
        fields={'address_line_1','address_line_2','city','state','country','profile_picture'}
    def __init__(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'


