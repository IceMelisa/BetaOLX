from django import forms
from .models import Product, Category, Review, UserProfile, City
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "cls"
            }
        )
    )
    firstname = forms.CharField(max_length=30, required=False)
    lastname = forms.CharField(max_length=30, required=False)
    phonenumber = forms.CharField(max_length=15, required=False)
    profilepicture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'firstname', 'lastname', 'phonenumber', 'profilepicture', 'password1', 'password2']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'image', 'city','adres']
        widgets = {
            'seller': forms.HiddenInput(attrs={'readonly': 'readonly'}),  

        }
    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # Добавить класс 'form-control' ко всем полям формы


class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="All Categories", required=False)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text','rating']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profilepicture', 'firstname', 'lastname']

class CityFilterForm(forms.Form):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label='Выберите город',
        required=False,
    )


