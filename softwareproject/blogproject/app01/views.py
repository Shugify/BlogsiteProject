from django.contrib.auth import login, authenticate
from django.http import HttpResponse
from django.shortcuts import render
from . import models, forms
from django.http import JsonResponse
from datetime import datetime  # 导入 datetime 模块


def home(request):
    pass
    return render(request, 'app01/home.html')


def index(request):
    pass
    return render(request, 'app01/index.html')


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


# 用户登录
def user_login(request):
    if request.method == 'POST':
        user_login_form = forms.UserLoginForm(request.POST)
        if user_login_form.is_valid():
            userid = user_login_form.cleaned_data.get('uid')
            password = user_login_form.cleaned_data.get('pwd')

            try:
                user = models.User.objects.get(user_id=userid)
            except models.User.DoesNotExist:
                return JsonResponse({'success': False, 'error_type': 'Nouid', 'error': 'id不存在'})

            if user.user_state == 1:
                return JsonResponse({'success': False, 'error_type': 'state', 'error': '该账号已封'})

            if user.user_password == password:
                # 记录登录态
                request.session['is_login'] = True
                request.session['user_id'] = user.user_id
                request.session['user_mail'] = user.user_mail
                request.session['user_phone'] = user.user_phone
                request.session['user_name'] = user.user_name
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error_type': 'wrongpwd', 'error': '密码错误'})
        else:
            return JsonResponse({'success': False, 'error_type': 'eempty', 'error': '存在未填项！'})
    else:
        return render(request, 'app01/index.html')


# 用户注册页面
def register(request):
    if request.method == 'POST':
        registration_form = forms.UserRegistrationForm(request.POST)
        if registration_form.is_valid():
            name = registration_form.cleaned_data.get('name')
            email = registration_form.cleaned_data.get('email')
            phone = registration_form.cleaned_data.get('phone')
            password = registration_form.cleaned_data.get('password')
            rpassword = registration_form.cleaned_data.get('rpassword')

            # 进行密码匹配验证
            if password != rpassword:
                return JsonResponse({'success': False, 'error_type': 'pwd_mismatch', 'error': '密码不匹配'})

            # 检查邮箱是否已经存在
            if models.User.objects.filter(user_mail=email).exists():
                return JsonResponse({'success': False, 'error_type': 'email_exists', 'error': '该邮箱已被注册'})

            # 检查电话是否已经存在
            if models.User.objects.filter(user_phone=phone).exists():
                return JsonResponse({'success': False, 'error_type': 'phone_exists', 'error': '该电话已被注册'})

            # 查询数据库中已有用户的数量
            existing_users_count = models.User.objects.count()
            # 自动生成新用户的 id 号
            # 查询数据库中最大的ID号
            max_user_id = models.User.objects.latest('user_id').user_id if existing_users_count > 0 else 100000

            # 自动生成新用户的 id 号
            new_user_id = int(max_user_id) + 1

            user_register_date = datetime.now()  # 获取注册时间
            try:
                user = models.User.objects.create(
                    user_id=new_user_id,
                    user_name=name,
                    user_mail=email,
                    user_phone=phone,
                    user_register=user_register_date,
                    user_state=0,
                    user_password=password
                )
                # 可以在这里执行其他逻辑，例如发送欢迎邮件等
                return JsonResponse({'success': True, 'message': '用户创建成功', 'new_user_id': new_user_id})
            except Exception as e:
                # 处理创建用户失败的情况
                return JsonResponse(
                    {'success': False, 'error_type': 'invalid', 'message': '用户创建失败', 'error': str(e)})
            # 可以选择记录登录态（例如注册后直接登录）

        else:
            return JsonResponse({'success': False, 'error_type': 'invalid_form', 'error': '表单填写不完整或格式不正确'})
    else:
        return render(request, 'app01/register.html')

#邮箱登录
def email_login(request):
    if request.method == 'POST':
        user_login_form = forms.UserEmailLoginForm(request.POST)
        if user_login_form.is_valid():
            email = user_login_form.cleaned_data.get('email')
            password = user_login_form.cleaned_data.get('pwd')

            try:
                user = models.User.objects.get(user_mail=email)
            except models.User.DoesNotExist:
                return JsonResponse({'success': False, 'error_type': 'Nouid', 'error': '账户不存在'})

            if user.user_state == 1:
                return JsonResponse({'success': False, 'error_type': 'state', 'error': '该账号已封'})

            if user.user_password == password:
                # 记录登录态
                request.session['is_login'] = True
                request.session['user_id'] = user.user_id
                request.session['user_mail'] = user.user_mail
                request.session['user_phone'] = user.user_phone
                request.session['user_name'] = user.user_name
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error_type': 'wrongpwd', 'error': '密码错误'})
        else:
            return JsonResponse({'success': False, 'error_type': 'eempty', 'error': '存在未填项！'})
    else:
        return render(request, 'app01/email_login.html')



#个人信息页
def self_center(request):
    pass
    return render(request, 'app01/self_center.html')



#管理员登录
def ad_login(request):
    pass
    return render(request, 'app01/ad_login.html')