import base64
import json
from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import (
    Category,
    Order,
    Prescription,
    Profile,
    UserBase,
    Drug,
    State,
)
from accounts.forms import AddPrescriptionImageForm, ChangePasswordForm, OrderForm, ProfileForm
from .serializers import (
    UserRegisterSerializer,
    UserSerializer,
    TokenObtainPairSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from rest_framework.parsers import MultiPartParser, FormParser

# Create your views here.


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(user.is_active) + str(timestamp)


account_activation_token = AccountActivationTokenGenerator()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Token authentication successful
            response.data["message"] = "Login successful"
        else:
            # Token authentication failed
            response.data["message"] = "Invalid credentials"
        return response

    # permission_classes = [AllowAny]

    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.validated_data['user']
    #     tokens = serializer.validated_data['tokens']

    #     # Customize the response data as per your requirements
    #     response_data = {
    #         'user_id': user.id,
    #         'username': user.username,
    #         'access_token': tokens.access_token,
    #         'refresh_token': tokens.refresh_token,
    #         'message': 'Login successful',
    #     }

    #     return Response(response_data)
    # def post(self, request, *args, **kwargs):
    #     if self.request.user:
    #         return super().post(request, *args, **kwargs)
    #     else:
    #         return Response({'detail':'Account not enabled'}, status=status.HTTP_401_UNAUTHORIZED)


# class RegisterUser(generics.CreateAPIView):
#     permission_classes = [AllowAny]

# queryset = UserBase.objects.all()
# serializer_class = UserRegisterSerializer


class RegisterUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        reg = UserRegisterSerializer(data=request.data)
        if reg.is_valid():
            newUser = reg.save()
            if newUser:
                self.send_activation_email(newUser)
                return Response(
                    {"message": "User registered successfully. Activation email sent."},
                    status=status.HTTP_201_CREATED,
                )
        error_message = "Registration failed. Please check the provided data."
        errors = reg.errors
        response_data = {"message": error_message, "errors": errors}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def send_activation_email(self, user):
        token = account_activation_token.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = reverse("activate", kwargs={"uidb64": uid, "token": token})
        activation_url = settings.BASE_URL + activation_link

        email_subject = "Activate your account"
        email_body = """
                        <html>
                            <body>
                                <h2>Activate your account</h2>
                                <p>Thank you for registering. Please click the following link to activate your account:</p>
                                <a href="{activation_url}">{activation_url}</a>
                            </body>
                        </html>
                    """.format(
            activation_url=activation_url
        )
        send_mail(
            email_subject,
            "",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=email_body,
        )

        return 1

    # def send_activation_email(self, user):
    #     token = account_activation_token.make_token(user)
    #     uid = urlsafe_base64_encode(force_bytes(user.pk))
    #     activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
    #     activation_url = settings.BASE_URL + activation_link

    #     return activation_url


class ActivateAccount(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        print('token', token, uidb64)
        try:
            uid = urlsafe_base64_decode(uidb64).decode("utf-8")
            print(uid, 'uid')
            user = UserBase.objects.get(pk=uid)
            print(user, 'this')
        except (TypeError, ValueError, OverflowError, UserBase.DoesNotExist):
            user = None

        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            # add profile verifed later
            user.save()
            return Response(
                {"message": "Account activated successfully.", "status":True},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "Invalid activation link.", "status":False},
                status=status.HTTP_400_BAD_REQUEST,
            )


# {"user_name":"daniska", "email":"abzm@gmail.com", "password":"abubakar", "password2":"abubakar"}


class Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        con = f"hey {request.user}"

        return Response({"response": con}, status=status.HTTP_200_OK)


class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.get_all_categories()
        return Response(data=categories, status=status.HTTP_200_OK)


class GetDrugs(APIView):
    def get(self, request):
        drugs = Drug.get_drugs_with_business_names()
        # print(drugs, 'drugs')
        return Response(data=drugs, status=status.HTTP_200_OK)


class GetPharmacies(APIView):
    def get(self, request):
        pharmacy = Profile.get_pharmacies()
        print(pharmacy, 'pharm')
        return Response(data=pharmacy, status=status.HTTP_200_OK)


class GetStates(APIView):
    def get(self, request):
        states = State.get_states()
        return Response(data=states, status=status.HTTP_200_OK)


class GetPharmacy(APIView):
    def get(self, request):
        pharmacy_id = request.GET.get("pharmacy_id")
        pharmacy = Profile.get_pharmacy(pharmacy_id=pharmacy_id)
        return Response(data=pharmacy, status=status.HTTP_200_OK)


class GetPharmacyDrugs(APIView):
    def get(self, request):
        pharmacy_id = request.GET.get("pharmacy_id")
        drugs = Drug.get_drugs_with_business_name(pharmacy_id=pharmacy_id)
        return Response(data=drugs, status=status.HTTP_200_OK)


class GetBestDrugs(APIView):
    def get(self, request):
        drugs = Drug.get_best_deals()
        # print(drugs, 'best')
        return Response(data=drugs, status=status.HTTP_200_OK)


class CreateOrderAPIView(APIView):
    def post(self, request, format=None):
        # form = OrderForm(request.POST)
        print("===Inner View=====")
        form = OrderForm(request.POST)
        print("====BEFORE========")
        # cart= json.loads(request.POST.get('cart'))

        # print('this', cart)

        if form.is_valid():
            order_data = dict(
                cart=form.cleaned_data["cart"],
                shipping_address=form.cleaned_data["shipping_address"],
                user_id=form.cleaned_data["userbase"],
                total_price=form.cleaned_data["total_price"],
                status=form.cleaned_data.get("status"),
                payment_info=form.cleaned_data["payment_info"],
            )

            order = Order.create_order(**order_data)

            if order:
                return Response(
                    {"message": "Order created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "Failed to create order"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            print(form.errors)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class SavePrescription(APIView):
    def post(self, request):
        form = AddPrescriptionImageForm(request.POST, request.FILES)
        if form.is_valid():
            dic = dict(
                drug_id=form.cleaned_data.get("drug_id", None),
                user_id=form.cleaned_data.get("user_id", None),
                prescription_image=form.cleaned_data.get("prescription_image", None),
            )
            print(dic)
            image = Prescription.save_uploaded_image(**dic)

            if image:
                return Response(
                    {"message": "Presription created successfully"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response(
                    {"message": "Failed to create image"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileAPIView(APIView):
    def post(self, request, format=None):
        # userbase_id = request.user.user_id # Assuming you're using authentication
        # print('inter', userbase_id)
        # update_data = request.data  # Assuming you're sending the update data in the request
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            userbase_id = form.cleaned_data.get("user_id")
            userbase_data = dict(
                first_name=form.cleaned_data.get("first_name"),
                phone=form.cleaned_data.get("phone"),
                last_name=form.cleaned_data.get("last_name"),
                image=form.cleaned_data.get("image"),
            )
            try:
                profile = Profile.update_profile(userbase_id, **userbase_data)
                if profile:
                    return Response(
                        {"message": "Profile updated successfully"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"message": "Profile not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )
            except Exception as e:
                print(e)
                return Response(
                    {"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)


class GetProfileAPIView(APIView):
    def get(self, request, userbase_id, *args, **kwargs):
        profile = Profile.get_profile(userbase_id)

        if profile:
            # Serialize the profile data if needed
            # profile_data = serialize_profile(profile)
            return Response({"profile": profile}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )


class GetStates(APIView):
    def get(self, request):
        states = State.get_states()
        # print(drugs, 'best')
        return Response(data=states, status=status.HTTP_200_OK)


class GetUser(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        profile = Profile.get_profile(user_id=user_id)
        if profile:
            return Response(data=profile, status=status.HTTP_200_OK)
        return Response({"message": "user not found"})


class GetOrder(APIView):
    def get(self, request):
        user_id = request.GET.get('user_id')
        order = Order.get_order(user_id=user_id)
        if order:
            return Response(data=order, status=status.HTTP_200_OK)
        return Response(data=[], status=status.HTTP_404_NOT_FOUND)


class ChangePasswordAPIView(APIView):
    def post(self, request):
        user_id = request.data.get("user_id")
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        dic = dict(
            user_id=user_id, 
            old_password=old_password,
            new_password=new_password
        )
    
        success, message = UserBase.change_password(**dic)

        
        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        else:
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)


class GetDrug(APIView):
    def get(self, request):
        drug_id = request.GET.get('drug_id')
        drug = Drug.get_drug(drug_id=drug_id)
        if drug:
            return Response(data=drug, status=status.HTTP_200_OK)
        return Response(data=[], status=status.HTTP_404_NOT_FOUND)

