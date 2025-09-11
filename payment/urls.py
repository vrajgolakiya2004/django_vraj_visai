from django.urls import path
from . import views
app_name = 'payment'

urlpatterns = [
    path('pricing/', views.PricingFun, name='pricingPage'),
    path('create-checkout-session/', views.CreateCheckoutSession, name='createCheckout'),
    path('webhook/', views.MyWebhookView, name='stripe-webhook'),
    path('success/', views.PaymentSuccess, name='payment-success'),
    path('cancel/', views.PaymentCancel, name='payment-cancel'),
]
