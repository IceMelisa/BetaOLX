from django.contrib import admin

from .models import UserProfile, Product, Category, UserProfile, Review, City

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(UserProfile, UserProfileAdmin)



admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(City)
