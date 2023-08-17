# from datetime import timezone
from django.utils import timezone
from django.db import models, transaction
from django.db.models import Q, F, Value
from django.utils.translation import gettext_lazy as _ 
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db.models.signals import post_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField
from django.contrib.auth.hashers import check_password
from django.db.models.fields import CharField
from django.db.models.functions import Concat, Coalesce
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
        states = cls.objects.all().values("id", "name", "state_id")
        return list(states)


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
    

    @classmethod
    def change_password(cls, user_id, old_password, new_password):
        try:
            user = cls.objects.get(id=user_id)
            if check_password(old_password, user.password):
                user.set_password(new_password)
                user.save()
                return True, "Password changed successfully."
            else:
                return False, "Incorrect old password."
        except cls.DoesNotExist:
            return False, "User not found."


class Profile(models.Model):
    userbase = models.OneToOneField('UserBase', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    business_image = models.URLField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    image = CloudinaryField(blank=True, null=True)
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
    
    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
    

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
            "lga__name",
            "userbase__email"
        ]

        return fields
    

    @classmethod
    def get_pharmacies(cls):
        pharmacies = cls.objects.filter(userbase__usertype='pharmacy').values(*cls.get_fields())
        for pharmacy in pharmacies:
            if pharmacy['image'] and hasattr(pharmacy['image'], 'url'):
                pharmacy['image'] = pharmacy['image'].url
            else:
                pharmacy['image'] = None
        # pharmacies = cls.objects.filter(userbase__usertype='pharmacy').annotate(
        # image_url=Concat(
        #     Coalesce('image', Value('')), Value(''), output_field=CharField()
        # )
        # ).values(*cls.get_fields(), 'image')

        print('model', pharmacies)
        return pharmacies
    
    @classmethod
    def get_pharmacy(cls, pharmacy_id, usertype="pharmacy"):
        try:
            pharmacy = cls.objects.filter(Q(id=pharmacy_id) & Q(userbase__usertype=usertype)).values(*cls.get_fields())
            for pharmac in pharmacy:
                if pharmac['image'] and hasattr(pharmac['image'], 'url'):
                    pharmac['image'] = pharmac['image'].url
                else:
                    pharmacy['image'] = None
            return pharmacy
        except cls.DoesNotExist:
            return None

    @classmethod
    def update_profile(cls, userbase_id, **kwargs):
        try:
            profile = cls.objects.get(userbase_id=userbase_id)
            for key, value in kwargs.items():
                setattr(profile, key, value)
            profile.save()
            return profile
        except cls.DoesNotExist:
            return None
    
    # def image_url(self):
    #     if self.image and hasattr(self.image, 'url'):
    #         return self.image.url
    
    # @classmethod 
    # def get_profile(cls, user_id):
    #     try:
    #         profile = cls.objects.filter(id=user_id).values(*cls.get_fields())
    #         return profile
    #     except cls.DoesNotExist:
    #         return None

    @classmethod
    def get_profile(cls, user_id):
        try:
            profile = cls.objects.filter(id=user_id).first()
            print(profile.image, 'pppp')
            if profile:
                profile_dict = {
                    "first_name": profile.first_name,
                    "image": profile.image_url(),
                    "last_name": profile.last_name,
                    "middle_name": profile.middle_name,
                    "phone": profile.phone,
                    "email": profile.userbase.email,
                    "state": profile.state.name
                    # ... include other fields here
                }
                return profile_dict
        except cls.DoesNotExist:
            return None
    

    # @classmethod
    # def get_profile(cls, userbase_id):
    #     try:
    #         profile = cls.objects.get(userbase_id=userbase_id)
    #         return profile
    #     except cls.DoesNotExist:
    #         return None


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    # image = models.ImageField(upload_to="image", default='default.jpg', blank=True)
    description = models.TextField()
    image = models.URLField(null=True, blank=True)
    

    def __str__(self):
        return self.name
    

    
    @classmethod
    def get_all_categories(cls):
        return cls.objects.all().values("id", "name", "description", "image")
    

class Drug(models.Model):
    name = models.CharField(max_length=255)
    images = models.JSONField(default=dict)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    pharmacy = models.ForeignKey('UserBase', on_delete=models.CASCADE)
    description = models.TextField(null=False, blank=False)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    stock = models.PositiveIntegerField(null=False, blank=False)
    image = CloudinaryField(blank=True, null=True)
    # image = models.ImageField(default="default.jpg", upload_to="image")
    # drug_image = models.ForeignKey("Images", on_delete=models.CASCADE)
    ratings = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)
    sold_out = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    pharmacy_profile = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    is_prescription_needed = models.BooleanField(default=False, blank=True, null=True)

    objects = DrugManager()

    def __str__(self):
        return f'{self.name}'
    
    @classmethod
    def get_fields(cls):
        fields = [
            "id",
            "name",
            "category__name",
            "pharmacy__business_name",
            "description",
            "original_price",
            "discount_price",
            "images",
            "image",
            "ratings",
            "created_at",
            "sold_out",
            "stock",
            # "pharmacy_profile__image",
            "pharmacy_profile__business_image",
            "pharmacy__created",
            "pharmacy__id"
        ]

        return fields

    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
    
    @classmethod
    def get_drugs_by_category(cls, category_id):
        return cls.objects.filter(category__id=category_id)
    
    @classmethod
    def get_drugs_with_business_names(cls):
        drugs = cls.objects.values(*cls.get_fields())
        for drug in drugs:
            if drug['image'] and hasattr(drug['image'], 'url'):
                drug['image'] = drug['image'].url
            else:
                drug['image'] = None
        return drugs

    @classmethod
    def get_drugs_with_business_name(cls, pharmacy_id):
        drugs = cls.objects.filter(pharmacy_id=pharmacy_id).values(*cls.get_fields())
        for dru in drugs:
            if dru['image'] and hasattr(dru['image'], 'url'):
                dru['image'] = dru['image'].url
            else:
                dru['image'] = None
        return list(drugs)
    
    @classmethod
    def get_best_deals(cls):
        return cls.objects.annotate(
            discount_percentage=(F('original_price') - F('discount_price')) / F('original_price') * 100
        ).order_by('discount_percentage')[:10].values(*cls.get_fields())

    @classmethod
    def get_drug(cls, drug_id):
        drug = cls.objects.filter(id=drug_id).values(*cls.get_fields())
        for dru in drug:
            if dru['image'] and hasattr(dru['image'], 'url'):
                dru['image'] = dru['image'].url
            else:
                dru['image'] = None
        return drug

# class Images(models.Model):
#     name = models.CharField(max_length=255)
#     public_id = models.CharField(max_length=255, null=False, blank=False)
#     url = models.URLField(null=False, blank=False)


    # def __str__(self):
    #     return f'{self.name}'

class Prescription(models.Model):
    userbase = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    drug = models.ForeignKey("Drug", on_delete=models.CASCADE)
    image = CloudinaryField(blank=True, null=True)


    def image_url(self):
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
    
    @classmethod
    def save_uploaded_image(cls, **kwargs):
        # Extract the necessary parameters from kwargs
        image = kwargs.get("prescription_image")
        print('image ppp')
        print(image)
        user_id = kwargs.get("user_id")
        drug_id = kwargs.get("drug_id")
        user = UserBase.objects.get(id=user_id)
        drug = Drug.objects.get(id=drug_id)
        prescription = cls(image=image, userbase=user, drug=drug)

            # Save the model instance
        prescription.save()

        return prescription

    @classmethod
    def get_image_url_by_drug_id(cls, drug_id):
        try:
            prescription_image = cls.objects.get(id=drug_id)
            return prescription_image.image_url()
        except cls.DoesNotExist:
            return None

    @classmethod
    def create_prescription(cls, userbase, drug, image_path):
        prescription = cls(
            userbase=userbase,
            drug=drug,
            image=image_path
        )
        prescription.save()
        return prescription


class Order(models.Model):
    STATUS_CHOICES = (
        ("Processing", "Processing"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
    )

    cart = models.JSONField(blank=True, null=True)
    shipping_address = models.JSONField()
    userbase = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Processing")
    payment_info = models.JSONField(null=True, blank=True)
    paid_at = models.DateTimeField(auto_now_add=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Order #{self.id}"
    
    @classmethod 
    def create_order(cls, **kwargs):
        with transaction.atomic():
            try:
                user_id = kwargs.pop("user_id", None)
                print('user id =======')
                print(user_id)
                image_path = kwargs.pop("image_path", None)
                cart = kwargs.pop("cart", {})
                shipping_address = kwargs.pop("shipping_address", {})
                total_price = kwargs.pop("total_price", 0.0)
                payment_info = kwargs.pop("payment_info", None)
                
                userbase = UserBase.objects.get(id=user_id)
               
                order = cls.objects.create(
                    cart=cart,
                    shipping_address=shipping_address,
                    userbase=userbase,
                    total_price=total_price,
                    # prescription=prescription,
                    payment_info=payment_info
                )
                # for drug_info in cart:
                #     drug_id = drug_info["drug_id"]
                #     quantity = drug_info["quantity"]
                    
                #     drug = Drug.objects.get(id=drug_id)
                #     drug.sold += quantity
                #     drug.stock -= quantity
                #     drug.save()
                drug_updates = []
                for item in cart:
                    print(item, 'oooo')
                    drug_id = item.get("id")
                    quantity = item.get("qty")

                    # Add an update for each drug in the cart
                    drug_updates.append(
                        Drug(
                            id=drug_id,
                            sold_out=F("sold_out") + quantity,  # Increase the sold count by the item's quantity
                            stock=F("stock") - quantity  # Decrease the stock count by the item's quantity
                        )
                    )
                print(drug_updates, 'updates')

                # Bulk update all the drugs in one query
                Drug.objects.bulk_update(drug_updates, fields=["sold_out", "stock"])

            

                return order

            except UserBase.DoesNotExist:
                raise ValueError(f"User with ID {user_id} does not exist")
            except Prescription.DoesNotExist:
                raise ValueError(f"Prescription does not exist")
    
    @classmethod
    def get_order(cls, user_id):
        try:
            orders = cls.objects.filter(userbase_id=user_id).values(
                "id",
                "cart",
                "shipping_address",
                "total_price",
                "status",
                "payment_info",
                "paid_at",
                "delivered_at",
                "created_at",
            )
            return list(orders)
        except cls.DoesNotExist:
            return []

class Payment(models.Model):
    user = models.ForeignKey(UserBase, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    # Add payment status and other relevant fields

    def __str__(self):
        return f"Payment by {self.user.user_name} for Order {self.order.id}"



    
    


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
    


