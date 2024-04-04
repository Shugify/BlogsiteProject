# 引入redirect重定向模块
import random
from datetime import datetime  # 导入 datetime 模块

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
# 引入HttpResponse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect

from . import models, forms
# 引入刚才定义的ArticleForm表单类
from .forms import ArticleForm
from .funcs import upload_file
from .models import Article
# 引入User模型
from .models import User
from django.contrib import messages


def home(request):
    # 获取按照浏览量排序的文章列表
    top_articles_views = Article.objects.all().order_by('-article_views')[:5]

    # 获取按照时间排序的文章列表
    top_articles_time = Article.objects.all().order_by('-article_created')[:5]

    # 获取随机排序的文章列表
    all_articles = list(Article.objects.all())
    random.shuffle(all_articles)
    top_articles_random = all_articles[:6]

    context = {
        'top_articles_views': top_articles_views,
        'top_articles_time': top_articles_time,
        'top_articles_random': top_articles_random
    }
    return render(request, 'app01/home.html', context)


def send_article(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticleForm(data=request.POST, files=request.FILES)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            if 'article_image' in request.FILES:
                # 调用 upload_file 函数处理文件上传
                upload_file(request)
            # 指定数据库当前用户为作者
            new_article.article_author = User.objects.get(user_id=request.user.user_id)
            # 将新文章保存到数据库中
            new_article.save()
            # 新增代码，保存 tags 的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到主页面
            return redirect("home")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticleForm()
        # 赋值上下文
        context = {'article_post_form': article_post_form}
        # 返回模板
        return render(request, 'app01/send_article.html', context)


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
                # 将用户数据保存在 session 中，即实现了登录动作
                login(request, user)
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


# 邮箱登录
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


# 个人信息页
def self_center(request):
    pass
    return render(request, 'app01/self_center.html')


# 管理员登录
def ad_login(request):
    pass
    return render(request, 'app01/ad_login.html')


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
