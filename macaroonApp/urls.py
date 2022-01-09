
from django.urls import path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

router = routers.DefaultRouter()

router.register(r'profile', views.ProfileView, 'profile')
router.register(r'group', views.CustomGroupViewSet, 'profile')

urlpatterns = [
    path('form/', views.MoneyForm.as_view()),
    path('oauthcallback/', views.OAuthCallback.as_view()),
    path('refresh/', views.RefreshJWT.as_view()),
    path('contacts/add/', views.AddContactAPIView.as_view()),
    path('contacts/list/', views.ListContactsAPIView.as_view()),
    path("transactions/sent/", views.TransactionsSent.as_view()),
    path("transactions/intermediary/", views.TransactionsReceivedAsIntermediary.as_view()),
    path("transactions/save/", views.SaveTransaction.as_view()),
    path("payments/sent/", views.FinalPaymentsSent.as_view()),
    path("payments/received/", views.FinalPaymentsReceived.as_view()),
    path("payments/save/", views.SaveFinalPayment.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += router.urls
