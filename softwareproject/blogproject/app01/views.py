from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    pass
    return render(request, 'app01/index.html')


def login(request):
    pass
    return render(request, 'app01/login.html')


def my_article(request):
    pass
    return render(request, 'app01/my_article.html')


def article(request):
    pass
    return render(request, 'app01/article.html')


def account_setting(request):
    pass
    return render(request, 'app01/account_setting.html')


def category(request):
    pass
    return render(request, 'app01/category.html')
