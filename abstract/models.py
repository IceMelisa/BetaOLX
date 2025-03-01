from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name='Номер телефона')  
    profilepicture = models.ImageField(upload_to='', blank=True, null=True, verbose_name='Фотография профиля')  
    firstname = models.CharField(max_length=30, blank=True, null=True, verbose_name='Имя')
    lastname = models.CharField(max_length=30, blank=True, null=True, verbose_name='Фамилия')

    def __str__(self):
        return self.user.username
     
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='', blank=True, verbose_name='Фотография')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Город')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Город'
        verbose_name_plural = 'Города' 

class Product(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(max_length=500, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    date_posted = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Продавец')
    image = models.ImageField(upload_to='', blank=True, verbose_name='Фотография')
    city = models.ForeignKey(City, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Город')
    adres = models.TextField(max_length='55', verbose_name='Адрес')
    
    



    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'



class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(
        default=5,
        validators=[
            MinValueValidator(1, message=_("Число для рейтинга не может быть ниже 1.")),
            MaxValueValidator(12, message=_("Число для рейтинга не может быть больше 12."))
        ],
        verbose_name='Рейтинг'
    )

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.title}"
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.username} - {self.product.title}'
    
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
