from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views  import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from accounts.models import Category, Profile, UserBase, Drug, State
from .serializers import UserRegisterSerializer, UserSerializer, TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes

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
            response.data['message'] = "Login successful"
        else:
            # Token authentication failed
            response.data['message'] = "Invalid credentials"
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
        print('heyyyyyyy')
        print(request.data)
        reg = UserRegisterSerializer(data=request.data)
        print('new', reg)
        if reg.is_valid():
            print('check')
            newUser = reg.save()
            if newUser:
                print('is validated', newUser)
                self.send_activation_email(newUser)
                return Response(
                    {"message": "User registered successfully. Activation email sent."},
                    status=status.HTTP_201_CREATED
                )
        error_message = "Registration failed. Please check the provided data."
        errors = reg.errors
        response_data = {"message": error_message, "errors": errors}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

    def send_activation_email(self, user):
        print('=======ACTIVATE========')
        print(user)
        token = account_activation_token.make_token(user)
        print('==========TOKEN')
        print(token)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        activation_url = settings.BASE_URL + activation_link
        print('================')
        print(uid, activation_link, activation_url)

        email_subject = "Activate your account"
        # email_body = render_to_string(
        #     'activation_email.html',
        #     {'activation_url': activation_url}
        # )
        email_body = """
                        <html>
                            <body>
                                <h2>Activate your account</h2>
                                <p>Thank you for registering. Please click the following link to activate your account:</p>
                                <a href="{activation_url}">{activation_url}</a>
                            </body>
                        </html>
                    """.format(activation_url=activation_url)
        send_mail(email_subject, '', settings.DEFAULT_FROM_EMAIL, [user.email], html_message=email_body)

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
        try:
            uid = urlsafe_base64_decode(uidb64).decode('utf-8')
            user = UserBase.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserBase.DoesNotExist):
            user = None

        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            # add profile verifed later
            user.save()
            return Response(
                {"message": "Account activated successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST
            )


# {"user_name":"daniska", "email":"abzm@gmail.com", "password":"abubakar", "password2":"abubakar"}

class Dashboard(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        con = f'hey {request.user}'

        return Response({'response': con}, status=status.HTTP_200_OK)


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
        # print(pharmacy, 'pharm')
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