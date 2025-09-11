from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('sign_up/', views.signUpFun, name='signUpPage'),
    path('signin/', views.signInFun, name='signInPage'),
    path('index/', views.indexFun, name='indexPage'),
    path('logout/', views.logoutFun, name='logoutPage'),
    path('user-profile/', views.userProfileFun, name='userProfilePage'),
    path('user-settings/', views.updateProfileFun, name='userSettingsPage'),
    path('password-change/', views.changePasswordFun, name='passwordChangePage'),
] 



