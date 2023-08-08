from django.contrib import admin
from .models import UserBase, Profile, Category, Drug, Images, State, LGA

# Register your models here.

@admin.register(UserBase)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_name', 'email']


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['userbase']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']


@admin.register(Images)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("name", "public_id", "url")


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(LGA)
class LgaAdmin(admin.ModelAdmin):
    list_display = ("name",)
