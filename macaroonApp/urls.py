from django.urls import path
from rest_framework import routers
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

router = routers.DefaultRouter()

router.register(r'profile', views.ProfileView, 'profile')

urlpatterns = [
    path('form/', views.MoneyForm.as_view()),
    path('oauthcallback/', views.OAuthCallback.as_view()),
    path('refresh/', views.RefreshJWT.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)

urlpatterns += router.urls
