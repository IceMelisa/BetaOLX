from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import product_list, create_product, product_detail, UserProfile, user_profile, register, login_view, filter_products, search_products, CategoryListView, ProductsByCategoryView, edit_product, delete_product, view_other_user_profile, custom_logout, city_list, ProductDetailView, SimilarProductsView, olx_products, add_to_favorites, favorites, remove_from_favorites
urlpatterns = [
    path('', product_list, name='product_list'),
    path('abs/<str:category>/', product_list, name='product_list_category'),
    path('products/create/', create_product, name='create_product'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('profile_page/', user_profile, name='user_profile_page'),
    path('register/', register, name='register'),
    path('login/', login_view, name='loginn'),
    path('filter/', filter_products, name='filter_products'),
    path('search/', search_products, name='search_products'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:category_id>/', ProductsByCategoryView.as_view(), name='products_by_category'),
    path('edit_product/<int:pk>/', edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', delete_product, name='delete_product'),
    path('profile/view/<str:username>/', view_other_user_profile, name='view_other_user_profile'),
    path('custom_logout/', custom_logout, name='custom_logout'),
    path('city_list/', city_list, name='city_list'),
    path('product/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('similar_products/<int:product_id>/', SimilarProductsView.as_view(), name='similar_products'),
    path('olx_products/', olx_products, name='olx_products'),
    path('add_to_favorites/<int:product_id>/', add_to_favorites, name='add_to_favorites'),
    path('favorites/', favorites, name='favorites'),
    path('remove_from_favorites/<int:product_id>/', remove_from_favorites, name='remove_from_favorites')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)