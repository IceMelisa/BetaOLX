from django.shortcuts import render, get_object_or_404
from django.shortcuts import render, redirect
from abstract.form import ProductForm, ProductFilterForm, RegistrationForm, ReviewForm, CategoryForm, CityFilterForm
from .models import Product, Category, Review, Favorite
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Product
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views import View
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.db.models import Avg
from bs4 import BeautifulSoup
from django.http import JsonResponse
import requests


def custom_login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return render(request, 'error_page.html', {'message': 'Вы не зарегистрированы. Зарегистрируйтесь, чтобы увидеть эту страницу.'})
    return _wrapped_view

@custom_login_required
def user_profile(request):
    user = request.user
    products = Product.objects.filter(seller=user)

    return render(request, 'user_profile_page.html', {'user': user, 'products': products})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('product_list')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def product_list(request):
    product_list = Product.objects.all()

    # Добавляем пагинацию
    page = request.GET.get('page', 1)
    paginator = Paginator(product_list, 10)  # 10 объявлений на каждой странице

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'product_list.html', {'products': products})





def filter_products(request):
    filter_category = request.GET.get('filter', None)
    categories = Category.objects.all()

    if filter_category:
        products = Product.objects.filter(category__name=filter_category)
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'filter_category': filter_category,
    }
    return render(request, 'product_list.html', context)

def search_products(request):
    search_query = request.GET.get('search', None)
    categories = Category.objects.all()

    if search_query:
        products = Product.objects.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query))
    else:
        products = Product.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'product_list.html', context)


@custom_login_required  # Это декоратор, который требует аутентификации пользователя
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Сохраняем форму, но перед этим устанавливаем seller на текущего пользователя
            product = form.save(commit=False)
            product.seller = request.user  # Устанавливаем seller на текущего пользователя
            product.save()
            return redirect('product_list')  # Перенаправляем на страницу со списком продуктов
    else:
        form = ProductForm()

    return render(request, 'create_product.html', {'form': form})



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product)

    # Рассчитываем среднюю цену в категории текущего товара
    category_avg_price = Product.objects.filter(category=product.category).aggregate(Avg('price'))['price__avg']

    # Обработка отправки отзыва
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            # Перенаправление для избежания повторной отправки формы
            return HttpResponseRedirect(request.path_info)
    else:
        form = ReviewForm()

    # Передаем результаты расчета и отзывы в контекст
    context = {
        'product': product,
        'avg_price_comparison': {
            'category_avg_price': category_avg_price,
            'is_cheaper': product.price < category_avg_price if category_avg_price else False,
        },
        'reviews': reviews,
        'form': form,
    }

    return render(request, 'product_detail.html', context)

class CategoryListView(View):
    template_name = 'category_list.html'

    def get(self, request):
        categories = Category.objects.all()
        return render(request, self.template_name, {'categories': categories})

class ProductsByCategoryView(View):
    template_name = 'products_by_category.html'

    def get(self, request, category_id):
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
        return render(request, self.template_name, {'category': category, 'products': products})
    
@custom_login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form, 'product': product})


@custom_login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Проверяем, что текущий пользователь является продавцом продукта
    if request.user != product.seller:
        messages.error(request, "Вы не можете удалить этот продукт.")
        return redirect('user_profile_page')  # Или замените на URL вашей профильной страницы

    # Обработка запроса POST для удаления продукта
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Продукт успешно удален.")
        return redirect('user_profile_page')  # Или замените на URL вашей профильной страницы

    return render(request, 'delete_product.html', {'product': product})




def view_other_user_profile(request, username):
    user = get_object_or_404(User, username=username)
    user_products = Product.objects.filter(seller=user)

    context = {
        'user': user,
        'user_products': user_products,
    }

    return render(request, 'view_other_user_profile.html', context)


def custom_logout(request):
    logout(request)
    # После выхода перенаправляем на главную страницу (можно изменить URL по вашему желанию)
    return redirect('product_list')

def city_list(request):
    # Если запрос GET, пытаемся фильтровать по городу
    if request.method == 'GET':
        form = CityFilterForm(request.GET)
        if form.is_valid():
            city = form.cleaned_data['city']
            # Фильтруем продукты по выбранному городу
            products = Product.objects.filter(city=city)
        else:
            # Если форма не валидна, выводим все продукты
            products = Product.objects.all()
    else:
        # Если запрос не GET, выводим все продукты
        products = Product.objects.all()
        form = CityFilterForm()

    return render(request, 'product_list.html', {'products': products, 'form': form})



class SimilarProductsView(View):
    template_name = 'similar_products.html'

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        current_product = get_object_or_404(Product, id=product_id)

        # Получите похожие товары (замените это на вашу логику выбора похожих товаров)
        similar_products = Product.objects.filter(category=current_product.category).exclude(id=product_id)[:10]

        context = {'similar_products': similar_products, 'current_product': current_product}
        return render(request, self.template_name, context)
    

class ProductDetailView(View):
    template_name = 'product_detail.html'

    def get(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        context = {'product': product}
        return render(request, self.template_name, context)
    
def parse_olx():
    url = 'https://www.olx.kz/'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = []

        # Пример: парсинг заголовков объявлений, цен и категорий
        titles = soup.select('.offer-titlebox h3 a')
        prices = soup.select('.price strong')
        categories = soup.select('.breadcrumb span a')

        for title, price, category in zip(titles, prices, categories):
            product = {
                'title': title.text.strip(),
                'price': price.text.strip(),
                'category': category.text.strip(),
            }
            products.append(product)

        return products
    else:
        return None

def olx_products(request):
    products = parse_olx()
    return render(request, 'olx_products.html', {'products': products})

@custom_login_required
def add_to_favorites(request, product_id):
    # Получаем объект товара
    product = get_object_or_404(Product, id=product_id)

    # Проверка, есть ли уже такой товар в избранном у пользователя
    existing_favorite = Favorite.objects.filter(user=request.user, product=product).exists()

    if not existing_favorite:
        # Если нет, то добавляем в избранное
        Favorite.objects.create(user=request.user, product=product)

    return redirect('product_list')  # Или замените на URL, куда вы хотите перенаправить после добавления в избранное


@custom_login_required
def favorites(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user)

    context = {'user': user, 'favorites': favorites}
    return render(request, 'favorites.html', context)

@custom_login_required
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    favorite = Favorite.objects.filter(user=request.user, product=product).first()

    if favorite:
        favorite.delete()

    return redirect('favorites')