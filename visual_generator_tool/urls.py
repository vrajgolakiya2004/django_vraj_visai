from django.urls import include, path
from django.contrib import admin
from . import views  
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.indexFun, name='homePage'),
    path('image-generation/', views.imageGenerationFun, name='imageGenerationPage'),
    path('payment/', include(('payment.urls', 'payment'), namespace='payment')),
    path('video-generation/', views.videoGenerationFun, name='videoGenerationPage'),
    path('documentation/', views.documentationFun, name='documentationPage'),
    path('faq/', views.faqFun, name='faqPage'),
    path('contact/', views.contactFun, name='contactPage'),
    path('user-billing/', views.userBillingFun, name='userBillingPage'),
    path('notification/', views.notificationFun, name='notificationPage'),
    path('', views.frontPageFun, name='frontPage'),
    path('index/', views.indexFun, name='indexPage'),
    path('register/', include('register.urls')), 
    path('rag/', include('rag.urls')),
    path('rag/api/', include('rag.api_urls')),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)