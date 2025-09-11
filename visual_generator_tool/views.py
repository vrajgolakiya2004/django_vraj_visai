from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt



def indexFun(request):
    return render(request, 'index.html')


def imageGenerationFun(request):
    return render(request, 'image-generation.html')


def videoGenerationFun(request):
    return render(request, 'video-generation.html')

def documentationFun(request):
    return render(request, 'documentation.html')

def faqFun(request):
    return render(request, 'faq.html')


def contactFun(request):
    return render(request, 'contact.html')


def userBillingFun(request):
    return render(request, 'user-billing.html')

def notificationFun(request):
    return render(request, 'notifications.html')


def frontPageFun(request): 
    return render(request, 'frontpage.html')


 
 
 