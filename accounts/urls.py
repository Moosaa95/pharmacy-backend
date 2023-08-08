from django.urls import path
from accounts.views import (RegisterUser, 
                            Dashboard, 
                            CustomTokenObtainPairView, 
                            ActivateAccount,
                            CategoryListAPIView,
                            GetDrugs,
                            GetPharmacies,
                            GetStates,
                            GetPharmacy,
                            GetPharmacyDrugs
                            )


from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/register/', RegisterUser.as_view(), name='register'),
    path('api/dashboard/', Dashboard.as_view(), name='dashboard'),
    path('api/activate/<str:uidb64>/<str:token>/', ActivateAccount.as_view(), name='activate'),
    path('categories/', CategoryListAPIView.as_view(), name='category-list'),
    path('drugs/', GetDrugs.as_view(), name='drugs'),
    path('pharmacies/', GetPharmacies.as_view(), name='pharmacies'),
    path('pharmacy/', GetPharmacy.as_view(), name='pharmacy'),
    path('pharmacydrugs/', GetPharmacyDrugs.as_view(), name='pharmacydrugs'),
    path('states/', GetStates.as_view(), name='states'),
]