# from datetime import timezone
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class DrugManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(business_name=models.F('pharmacy__business_name'))


class CustomAccountManager(BaseUserManager):

    # @staticmethod
    def create_superuser(self, email, user_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True'
            )
        
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True'
            )

        return self.create_user(email, user_name, password, **other_fields)
    
    # @staticmethod
    def create_user(self, email, user_name, password, **other_fields):

        if not email:
            raise ValueError(_('You must must provide an email address'))
        
        email = self.normalize_email(email)
        user =  self.model(email=email, user_name=user_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class State(models.Model):
    name = models.CharField(max_length=50)
    state_id = models.CharField(max_length=50)


    def __str__(self):
        return f'{self.name}'

    @classmethod
    def get_states(cls):
        states = cls.objects.all().values()
        return states


class LGA(models.Model):
    name = models.CharField(max_length=50)
    state_id = models.ForeignKey('State', on_delete=models.CASCADE)



class UserBase(AbstractBaseUser, PermissionsMixin):
    USER_CHOICES = (
        ('user', 'user'),
        ('pharmacy', 'pharmacy')

    )
    email = models.EmailField(_('email address'), unique=True)
    user_name = models.CharField(max_length=150, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    usertype = models.CharField(max_length=50, choices=USER_CHOICES, blank=True, null=True) #TODO remove blank and null from true later
    state = models.ForeignKey('State', on_delete=models.SET_NULL, blank=True, null=True)
    lga = models.ForeignKey('LGA', on_delete=models.SET_NULL, blank=True, null=True)
    business_name = models.CharField(max_length=200, blank=True, null=True)
    


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    objects = CustomAccountManager()

    class Meta:
        verbose_name = "Accounts"
        verbose_name_plural = "Accounts"
        
    def __str__(self):
        return self.email


class Profile(models.Model):
    userbase = models.OneToOneField('UserBase', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to="image", default='default.jpg', blank=True)
    bio = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    verified = models.BooleanField(default=False)
    business_name = models.CharField(max_length=200, blank=True, null=True)
    state = models.ForeignKey('State', on_delete=models.SET_NULL, blank=True, null=True)
    lga = models.ForeignKey('LGA', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return f'{self.userbase.user_name} '

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
    

    @classmethod
    def get_fields(cls):
        fields = [
            "id",
            "first_name",
            "last_name",
            "image",
            "bio",
            "phone",
            "verified",
            "business_name",
            "state__name",
            "lga__name"
        ]

        return fields
    

    @classmethod
    def get_pharmacies(cls):
        return cls.objects.filter(userbase__usertype='pharmacy').values(*cls.get_fields())
    
    @classmethod
    def get_pharmacy(cls, pharmacy_id, usertype="pharmacy"):
        try:
            pharmacy = cls.objects.filter(Q(id=pharmacy_id) & Q(userbase__usertype=usertype)).values(*cls.get_fields())
            return pharmacy
        except cls.DoesNotExist:
            return None

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to="image", default='default.jpg', blank=True)
    description = models.TextField()
    

    def __str__(self):
        return self.name
    

    
    @classmethod
    def get_all_categories(cls):
        return cls.objects.all().values()
    

class Drug(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey('UserBase', on_delete=models.CASCADE)
    description = models.TextField(null=False, blank=False)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    stock = models.PositiveIntegerField(null=False, blank=False)
    # image = models.ImageField(default="default.jpg", upload_to="image")
    drug_image = models.ForeignKey("Images", on_delete=models.CASCADE)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    sold_out = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = DrugManager()

    def __str__(self):
        return f'{self.name}'
    
    @classmethod
    def get_fields(cls):
        fields = [
            "name",
            "category__name",
            "pharmacy__business_name",
            "description",
            "original_price",
            "discount_price",
            "drug_image__url",
            "ratings",
            "created_at",
            "sold_out",
            "stock"
        ]

        return fields
    

    @classmethod
    def get_drugs_with_business_names(cls):
        return list(cls.objects.values(*cls.get_fields()))

    @classmethod
    def get_drugs_with_business_name(cls, pharmacy_id):
        drugs = cls.objects.filter(pharmacy_id=pharmacy_id).values(*cls.get_fields())
        return list(drugs)


class Images(models.Model):
    name = models.CharField(max_length=255)
    public_id = models.CharField(max_length=255, null=False, blank=False)
    url = models.URLField(null=False, blank=False)


    def __str__(self):
        return f'{self.url}'

class Prescription(models.Model):
    userbase = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    drug = models.ForeignKey("Drug", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image", default="default.jpg")


    @classmethod
    def create_prescription(cls, userbase, drug, image_path):
        prescription = cls(
            userbase=userbase,
            drug=drug,
            image=image_path
        )
        prescription.save()
        return prescription

# class Order(models.Model):
#     STATUS = (
#         ("pending", "Pending"),
#         ("in_progress", "In Progress"),
#         ("completed", "Completed")
#     )
#     userbase = models.ForeignKey(UserBase, on_delete=models.CASCADE)
#     drug = models.ForeignKey("Drug", on_delete=models.SET_NULL)
#     pharmacy = models.ForeignKey(UserBase, on_delete=models.CASCADE, related_name='orders_received')
#     quantity = models.PositiveIntegerField(default=0)
#     status = models.CharField(choices=STATUS, max_length=20)
#     prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    
    
#     @classmethod
#     def create_order_with_prescription(cls, userbase, drug, pharmacy, prescription, quantity, status):
#         order = cls(
#             userbase=userbase,
#             drug=drug,
#             pharmacy=pharmacy,
#             prescription=prescription,
#             quantity=quantity,
#             status="pending"
#         )
#         order.save()
#         return order
class Order(models.Model):
    STATUS_CHOICES = (
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
    )

    cart = models.JSONField()
    shipping_address = models.JSONField()
    userbase = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Processing")
    payment_info = models.JSONField(null=True, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)


    def __str__(self):
        return f"Order #{self.id}"




    
    


# @receiver(post_save, sender=UserBase)
# def create_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(userbase=instance)

# @receiver(post_save, sender=UserBase)
# def save_profile(sender, instance, **kwargs):
#     instance.profile.save()

# @receiver(post_save, sender=UserBase)
# def create_or_save_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(userbase=instance)
#     else:
#         profile = instance.profile

#     if instance.usertype == 'pharmacy':
#         profile.business_name = 'Default Business Name'  # Set the default business name for pharmacy users
#     else:
#         profile.business_name = 'new better'

#     profile.save()

# @receiver(post_save, sender=UserBase)
# def create_or_save_profile(sender, instance, created, **kwargs):
#     if created:
#         profile = Profile.objects.create(userbase=instance)
#     else:
#         profile = instance.profile

#     if instance.usertype == 'pharmacy':
#         profile.business_name = 'Default Business Name'  # Set the default business name for pharmacy users
#     else:
#         profile.business_name = 'new yorker'

#     profile.save()

# @receiver(post_save, sender=UserBase)
# def create_or_save_profile(sender, instance, created, **kwargs):
#     profile = instance.profile if hasattr(instance, 'profile') else None

#     if created:
#         profile = Profile.objects.create(userbase=instance)

#     if profile:
#         if instance.usertype == 'pharmacy':
#             profile.business_name = 'Default Business Name'  # Set the default business name for pharmacy users
#         else:
#             profile.business_name = None

#         profile.save()
    
