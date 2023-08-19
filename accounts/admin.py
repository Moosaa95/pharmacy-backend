from django.contrib import admin
from .models import (UserBase, Profile, Category,
                      Drug,  State, LGA, Order, Prescription)
from django.contrib.auth import get_user_model

User = get_user_model()

# Register your models here.

@admin.register(User)
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


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("drug", "userbase", "image")


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(LGA)
class LgaAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("userbase", "status", "total_price", "paid_at")
