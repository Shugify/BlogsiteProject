# 引入redirect重定向模块
import random
from datetime import datetime  # 导入 datetime 模块

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
# 引入HttpResponse
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from . import models, forms
# 引入刚才定义的ArticleForm表单类
from .forms import ArticleForm, CommentForm
from .funcs import upload_file
from .models import Article, Comment, Category, ArticleCategory, Administrator
# 引入分页模块
from django.core.paginator import Paginator

import os
from django.contrib.auth import logout as django_logout
from django.utils import timezone

# 引入 Q 对象
from django.db.models import Q

from django.db.models import Max
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Category, User, Article
from .forms import ArticleForm


# 首页
def index(request):
    pass
    return render(request, 'app01/index.html')


def home(request):
    # 获取按照浏览量排序的文章列表
    top_articles_views = Article.objects.filter(article_author__isnull=False).order_by('-article_views')[:5]

    # 获取按照时间排序的文章列表
    top_articles_time = Article.objects.filter(article_author__isnull=False).order_by('-article_created')

    # 获取随机排序的文章列表
    all_articles = list(Article.objects.filter(article_author__isnull=False))
    random.shuffle(all_articles)
    top_articles_random = all_articles

    # 获取管理员发布的文章列表
    admin_articles = Article.objects.filter(article_adAuthor__isnull=False).order_by('-article_created')

    context = {
        'top_articles_views': top_articles_views,
        'top_articles_time': top_articles_time,
        'top_articles_random': top_articles_random,
        'admin_articles': admin_articles,
    }
    return render(request, 'app01/home.html', context)


def send_article(request):
    categories = Category.objects.all()
    if request.method == "POST":
        article_post_form = ArticleForm(data=request.POST, files=request.FILES)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            if 'article_image' in request.FILES:
                # 假设 upload_file 是你自定义的处理上传文件的函数
                upload_file(request)

            # 获取当前登录用户并设置为文章作者
            new_article.article_author = User.objects.get(user_id=request.user.user_id)

            # 将新文章保存到数据库中
            new_article.save()

            # 保存 tags 的多对多关系
            article_post_form.save_m2m()

            # 处理分类的保存
            selected_categories = article_post_form.cleaned_data.get('categories')
            if selected_categories:
                for category in selected_categories:
                    ArticleCategory.objects.create(article=new_article, category=category)

            return redirect("home")
        else:
            print(article_post_form.errors)
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticleForm()

    context = {
        'article_post_form': article_post_form,
        'categories': categories,
    }

    return render(request, 'app01/send_article.html', context)


# 用户登录页
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


# 用户注册页
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

            # 检查数据库中最大的用户ID
            try:
                # 使用aggregate来避免QuerySet为空时引发异常
                max_user_id = models.User.objects.aggregate(max_id=Max('user_id'))['max_id']
                if max_user_id is None:  # 如果max_id为None，则数据库中没有用户
                    max_user_id = 0
                else:
                    max_user_id = int(max_user_id)
            except models.User.DoesNotExist:  # Django ORM本身不会抛出DoesNotExist异常，但确保安全
                max_user_id = 0
            print("max_user_id:", max_user_id)

            if max_user_id < 1000000:
                new_user_id = 1000001
            else:
                new_user_id = max_user_id + 1
            while models.User.objects.filter(user_id=new_user_id).exists():
                new_user_id += 1
            # 自动生成新用户的 id

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


# 邮箱登录页
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


# 管理员登录
def ad_login(request):
    pass
    return render(request, 'app01/ad_login.html')


# 个人博客页面文章列举
def my_article(request):
    # 获取特定用户
    user = models.User.objects.get(user_id=request.session['user_id'])
    # 获取该用户的所有文章
    article_list = models.Article.objects.filter(article_author=user)
    # 每页显示 3 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    return render(request, 'app01/my_article.html', locals())


# 文章修改页
def update_article(request, id):
    # 获取需要修改的具体文章对象与作者
    article = models.Article.objects.get(article_id=id)
    author = article.article_author
    author_name = article.article_author.user_name
    # 过滤非作者的用户
    if request.user != article.article_author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = forms.ArticleForm(request.POST, request.FILES)
        # 使用Django内置的方法，判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、content,image,tags 数据并保存
            article.article_title = request.POST['article_title']
            article.article_content = request.POST['article_content']
            if request.FILES.get('article_image'):
                article.article_image = request.FILES.get('article_image')
            # 获取标签字符串
            tag_string = request.POST.get('tags')
            # 分割标签字符串并去除空格，注意是用英文逗号分割
            tags_list = [tag.strip() for tag in tag_string.split(',')]
            # 清除当前文章的所有标签
            article.tags.clear()
            # 设置文章的新标签
            article.tags.add(*tags_list)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = forms.ArticleForm()
        # 赋值上下文
        context = {
            'article': article,
            'id': id,
            'author_name': author_name,
            'author': author,
            'article_post_form': article_post_form,
        }
        # 返回模板
        return render(request, 'app01/update_article.html', context)


# 文章删除页
def delete_article(request, id):
    # 根据 id 获取需要删除的文章
    article = models.Article.objects.get(article_id=id)
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回个人文章列表
    return redirect("my_article")


# 文章详情页
def article_detail(request, id):
    # 取出相应的文章
    article = get_object_or_404(Article, article_id=id)
    # 获取文章的作者
    flag = False
    # 文章作者是管理员
    if article.article_author is None:
        flag = True
        author = article.article_adAuthor
        author_name = article.article_adAuthor.administrator_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_adAuthor=author).count()
        # 获取最新的用户信息
        user = article.article_adAuthor
        user_register_date = user.administrator_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 文章作者是普通用户
    else:
        author = article.article_author
        author_name = article.article_author.user_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_author=author).count()
        # 获取最新的用户信息
        user = article.article_author
        user_register_date = user.user_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 获取按照浏览量排序的文章列表,排除本篇
    top_articles_views = Article.objects.exclude(article_id=id).order_by('-article_views')[:5]
    # 检查是否有热门文章
    if not top_articles_views.exists():
        no_top_articles = True
    else:
        no_top_articles = False
    # 取出文章评论
    comments = Comment.objects.filter(comment_article=article)
    # 浏览量+1
    article.article_views += 1
    article.save(update_fields=['article_views'])
    # 计算评论数量
    article_commentcnt = comments.count()
    article.article_commentcnt = article_commentcnt
    article.save(update_fields=['article_commentcnt'])

    # 字典，内容要传递给模版
    context = {'article': article,
               'author': author,
               'author_name': author_name,
               'post_id': article.article_id,  # 确保 post_id 传递给模板
               'comments': comments,
               'article_commentcnt': article_commentcnt,
               'author_article_count': author_article_count,  # 传递作者文章总数给模板
               'days_diff': days_diff,  # 传递注册天数
               'top_articles_views': top_articles_views,  # 传递热门文章
               'no_top_articles': no_top_articles,
               'flag': flag
               }
    # 载入模板，并返回context对象
    return render(request, 'app01/article.html', context)


# 发表评论
@login_required(login_url='/login/')
def post_comment(request, article_id):
    article = get_object_or_404(Article, article_id=article_id)
    if request.method == 'POST':
        # 用户提交的数据存在 request.POST 中，这是一个类字典对象。
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            # 设置评论所属的文章和用户
            new_comment.comment_article = article
            new_comment.comment_user = request.user
            new_comment.save()  # comment_created 将在此时自动设置为当前时间
            # 可以重定向或渲染相同页面
            return redirect(reverse('article', kwargs={'id': article_id}))
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 处理错误请求
    else:
        return HttpResponse("发表评论仅接受POST请求。")


# 个人发表的评论列举页
def my_comment(request):
    # 获取特定用户
    user = models.User.objects.get(user_id=request.session['user_id'])
    # 获取该用户发表的所有评论
    comment_list = models.Comment.objects.filter(comment_user=user)
    # 每页显示 5 条评论
    paginator = Paginator(comment_list, 5)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 comments
    comments = paginator.get_page(page)
    return render(request, 'app01/my_comment.html', locals())


# 获得他人的评论列举页
def other_comment(request):
    # 获取特定用户
    user = models.User.objects.get(user_id=request.session['user_id'])
    # 获取该用户收到的所有评论
    comment_list = models.Comment.objects.filter(comment_article__article_author=user)
    # 去除自己给自己的评论
    comment_list = comment_list.exclude(comment_user=user)
    # 每页显示 5 条评论
    paginator = Paginator(comment_list, 5)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 comments
    comments = paginator.get_page(page)
    return render(request, 'app01/other_comment.html', locals())


# 在评论管理页面点击评论跳转并滚动到评论所在位置
def comment_detail(request, article_id, comment_id):
    # 取出相应的文章
    article = get_object_or_404(Article, article_id=article_id)
    # 获取文章的作者
    flag = False
    # 文章作者是管理员
    if article.article_author is None:
        flag = True
        author = article.article_adAuthor
        author_name = article.article_adAuthor.administrator_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_adAuthor=author).count()
        # 获取最新的用户信息
        user = article.article_adAuthor
        user_register_date = user.administrator_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 文章作者是普通用户
    else:
        author = article.article_author
        author_name = article.article_author.user_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_author=author).count()
        # 获取最新的用户信息
        user = article.article_author
        user_register_date = user.user_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 获取按照浏览量排序的文章列表,排除本篇
    top_articles_views = Article.objects.exclude(article_id=article_id).order_by('-article_views')[:5]
    # 检查是否有热门文章
    if not top_articles_views.exists():
        no_top_articles = True
    else:
        no_top_articles = False
    # 取出文章评论
    comments = Comment.objects.filter(comment_article=article)
    # 浏览量+1
    article.article_views += 1
    article.save(update_fields=['article_views'])
    # 计算评论数量
    article_commentcnt = comments.count()
    article.article_commentcnt = article_commentcnt
    article.save(update_fields=['article_commentcnt'])

    # 字典，内容要传递给模版
    context = {'article': article,
               'author': author,
               'author_name': author_name,
               'post_id': article.article_id,  # 确保 post_id 传递给模板
               'comments': comments,
               'comment_id': comment_id,  # comment_id传过去才能滚动定位
               'article_commentcnt': article_commentcnt,
               'author_article_count': author_article_count,  # 传递作者文章总数给模板
               'days_diff': days_diff,  # 传递注册天数
               'top_articles_views': top_articles_views,  # 传递热门文章
               'no_top_articles': no_top_articles,
               'flag': flag,
               }
    # 载入模板，并返回context对象
    return render(request, 'app01/comment_detail.html', context)


# 评论删除页
def delete_comment(request, id):
    # 根据 id 获取需要删除的评论
    comment = models.Comment.objects.get(comment_id=id)
    # 调用.delete()方法删除评论
    comment.delete()
    # 完成删除后返回个人评论列表
    return redirect("my_comment")


# def article(request):
#     pass
#     return render(request, 'app01/article.html')

# 个人信息页
def account_setting(request):
    if request.method == 'POST':
        field_name = request.POST.get('field_name')
        new_value = request.POST.get('new_value')
        # print("field_name:", field_name)
        # print("new_value:", new_value)
        # 在这里处理并保存更新后的数据到数据库中
        # 例如：
        user = models.User.objects.get(user_id=request.session['user_id'])

        if field_name == 'user_name':
            user.user_name = new_value
        elif field_name == 'user_introduction':
            user.user_introduction = new_value
        elif field_name == 'user_ip':
            user.user_ip = new_value
        elif field_name == 'user_sex':
            if new_value == '男':
                user.user_sex = 1
            else:
                user.user_sex = 0
        elif field_name == 'user_birthday':
            user.user_birthday = new_value
            birthdate = datetime.strptime(new_value, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            user.user_age = age

        user.save()

        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
    elif request.method == 'GET':

        # 获取最新的用户信息
        user = User.objects.get(user_id=request.session['user_id'])
        user_register_date = user.user_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数

        context = {
            'days_diff': days_diff,
        }
        return render(request, 'app01/account_setting.html', context)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# 账号信息显示页
def account_setting1(request):
    if request.method == 'POST':
        field_name = request.POST.get('field_name')
        new_value = request.POST.get('new_value')
        # print("field_name:", field_name)
        # print("new_value:", new_value)
        # 在这里处理并保存更新后的数据到数据库中
        # 例如：
        user = models.User.objects.get(user_id=request.session['user_id'])

        if field_name == 'user_phone':
            # 检查电话是否已经存在
            if new_value != user.user_phone and models.User.objects.filter(user_phone=new_value).exists():
                return JsonResponse({'success': False, 'error_type': 'phone_exists', 'message': 'phone exist'})
            user.user_phone = new_value
        elif field_name == 'user_mail':
            # 检查邮箱是否已经存在
            if new_value != user.user_mail and models.User.objects.filter(user_mail=new_value).exists():
                return JsonResponse({'success': False, 'error_type': 'email_exists', 'message': 'mail exist'})
            user.user_mail = new_value

        user.save()

        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
    elif request.method == 'GET':
        return render(request, 'app01/account_setting1.html')
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# 用户头像信息更新
def upload_user(request):
    if request.method == 'POST':
        try:
            avatar = request.FILES['avatar']
            filename, ext = os.path.splitext(avatar.name)

            # 获取当前用户的ID作为文件名前缀
            user_id = request.session.get('user_id')
            ext = '.jpg'

            unique_filename = f"{user_id}_portrait{ext}"

            with open(f'app01/static/app01/image/myimage/{unique_filename}', 'wb') as destination:
                for chunk in avatar.chunks():
                    destination.write(chunk)

            # 更新数据库中用户的头像路径
            user = User.objects.get(user_id=user_id)
            user.user_pfp = f'app01/static/app01/image/myimage/{unique_filename}'
            user.save()

            user = User.objects.get(user_id=request.session['user_id'])
            user_register_date = user.user_register  # 假设这是用户注册的日期
            current_date = timezone.now().date()  # 获取当前日期
            days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数

            context = {
                'days_diff': days_diff,
            }
            return render(request, 'app01/account_setting.html', context)
        except KeyError:
            # 如果没有选择文件，则返回错误消息
            error_message = "请选择要上传的文件"
            return render(request, 'app01/account_setting.html', {'error_message': error_message})

    else:
        # 如果不是 POST 请求，则重定向到个人信息页面
        return render(request, 'app01/account_setting.html')


# 修改密码
def account_setting1_password(request):
    if request.method == 'POST':
        change_pwd_form = forms.UserChangePwdForm(request.POST)
        if change_pwd_form.is_valid():
            old_password = change_pwd_form.cleaned_data.get('oldPassword')
            new_password = change_pwd_form.cleaned_data.get('newPassword')
            check_password = change_pwd_form.cleaned_data.get('checkPassword')

            print("get form successfully", new_password)

            user = models.User.objects.get(user_id=request.session['user_id'])

            # 进行密码匹配验证
            if new_password != check_password:
                return JsonResponse({'success': False, 'error_type': 'pwdMismatch', 'error': '密码不匹配'})

            if old_password == user.user_password:
                user.user_password = new_password
                user.save()
                print("save success", new_password)
                return JsonResponse({'success': True, 'message': '密码修改成功'})
            else:
                print("old pwd error")
                return JsonResponse({'success': False, 'error_type': 'old_pwd_error', 'error': '原密码错误'})
        else:
            print("form error")
            return JsonResponse({'success': False, 'error_type': 'invalidForm', 'error': '表单填写不完整或格式不正确'})
    else:
        return render(request, 'app01/account_setting1_password.html')


def logout(request):
    django_logout(request)
    request.session.clear()
    return JsonResponse({'success': True})


def dispose_account(request):
    user = models.User.objects.get(user_id=request.session['user_id'])
    user.user_state = 1
    user.save()
    django_logout(request)
    request.session.clear()
    return JsonResponse({'success': True})


def category(request):
    pass
    return render(request, 'app01/category.html')


def search_results(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    # 初始化查询集
    article_list = Article.objects.all()

    # 搜索查询集
    if search:
        if order == 'article_views':
            article_list = article_list.filter(
                Q(article_title__icontains=search) |
                Q(article_content__icontains=search) |
                Q(tags__name__icontains=search)
            ).order_by('-article_views')
        else:
            article_list = article_list.filter(
                Q(article_title__icontains=search) |
                Q(article_content__icontains=search) |
                Q(tags__name__icontains=search)
            )
    else:
        # 将 search 参数重置为空
        search = ''
    # 查询集排序
    # 按热度排序博文

    # 每页显示 1 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = {
        'articles': articles,
        'order': order,
        'search': search,
    }
    # render函数：载入模板，并返回context对象
    return render(request, 'app01/search.html', context)


# 管理员登录
def ad_login(request):
    if request.method == 'POST':
        administrator_login_form = forms.ADLoginForm(request.POST)
        if administrator_login_form.is_valid():
            aid = administrator_login_form.cleaned_data.get('aid')
            password = administrator_login_form.cleaned_data.get('pwd')

            try:
                administrator = models.Administrator.objects.get(administrator_id=aid)
            except models.Administrator.DoesNotExist:
                return JsonResponse({'success': False, 'error_type': 'Nouid', 'error': 'id不存在'})

            if administrator.administrator_password == password:
                # 记录登录态
                # 将数据保存在 session 中，即实现了登录动作

                request.session['is_login'] = True
                request.session['administrator_id'] = administrator.administrator_id
                request.session['administrator_mail'] = administrator.administrator_mail
                request.session['administrator_phone'] = administrator.administrator_phone
                request.session['administrator_name'] = administrator.administrator_name

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error_type': 'wrongpwd', 'error': '密码错误'})
        else:
            return JsonResponse({'success': False, 'error_type': 'eempty', 'error': '存在未填项！'})
    else:
        return render(request, 'app01/ad_login.html')


# 管理员主页面，用于管理用户账户
def ad_home(request):
    pass
    return render(request, 'app01/ad_home.html')


# 管理员账号信息显示页
def ad_account_setting(request):
    if request.method == 'POST':
        field_name = request.POST.get('field_name')
        new_value = request.POST.get('new_value')
        # print("field_name:", field_name)
        # print("new_value:", new_value)
        # 在这里处理并保存更新后的数据到数据库中
        # 例如：
        administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])

        if field_name == 'administrator_name':
            administrator.administrator_name = new_value
        elif field_name == 'administrator_introduction':
            administrator.administrator_introduction = new_value
        elif field_name == 'administrator_ip':
            administrator.administrator_ip = new_value
        elif field_name == 'administrator_sex':
            if new_value == '男':
                administrator.administrator_sex = 1
            else:
                administrator.administrator_sex = 0
        elif field_name == 'administrator_birthday':
            administrator.administrator_birthday = new_value
            birthdate = datetime.strptime(new_value, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            administrator.administrator_age = age

        administrator.save()

        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
    elif request.method == 'GET':

        # 获取最新的用户信息
        administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
        administrator_register_date = administrator.administrator_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - administrator_register_date).days  # 计算注册到当前的天数

        context = {
            'days_diff': days_diff,
            'administrator_name': administrator.administrator_name,
            'administrator_id': administrator.administrator_id,
            'administrator_introduction': administrator.administrator_introduction,
            'administrator_sex': administrator.administrator_sex,

            'administrator_birthday': administrator.administrator_birthday,
            'administrator_age': administrator.administrator_age,
            'administrator_ip': administrator.administrator_ip,
            'administrator_register': administrator.administrator_register,
            'administrator_pfp': administrator.administrator_pfp,

        }
        return render(request, 'app01/ad_account_setting.html', context)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# 管理员头像信息更新
def upload_administrator(request):
    if request.method == 'POST':
        try:
            avatar = request.FILES['avatar']
            filename, ext = os.path.splitext(avatar.name)

            # 获取当前用户的ID作为文件名前缀
            administrator_id = request.session.get('administrator_id')
            ext = '.jpg'

            unique_filename = f"{administrator_id}_portrait{ext}"

            with open(f'app01/static/app01/image/myimage/{unique_filename}', 'wb') as destination:
                for chunk in avatar.chunks():
                    destination.write(chunk)

            # 更新数据库中用户的头像路径
            administrator = models.Administrator.objects.get(administrator_id=administrator_id)
            administrator.administrator_pfp = f'app01/static/app01/image/myimage/{unique_filename}'
            administrator.save()

            administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
            administrator_register_date = administrator.administrator_register  # 假设这是用户注册的日期
            current_date = timezone.now().date()  # 获取当前日期
            days_diff = (current_date - administrator_register_date).days  # 计算注册到当前的天数

            context = {
                'days_diff': days_diff,
                'administrator_name': administrator.administrator_name,
                'administrator_id': administrator.administrator_id,
                'administrator_introduction': administrator.administrator_introduction,
                'administrator_sex': administrator.administrator_sex,

                'administrator_birthday': administrator.administrator_birthday,
                'administrator_age': administrator.administrator_age,
                'administrator_ip': administrator.administrator_ip,
                'administrator_register': administrator.administrator_register,
                'administrator_pfp': administrator.administrator_pfp,
            }
            return render(request, 'app01/ad_account_setting.html', context)
        except KeyError:
            # 如果没有选择文件，则返回错误消息
            error_message = "请选择要上传的文件"
            return render(request, 'app01/ad_account_setting.html', {'error_message': error_message})

    else:
        # 如果不是 POST 请求，则重定向到个人信息页面
        return render(request, 'app01/ad_account_setting.html')


# 管理员账号信息显示页
def ad_account_setting1(request):
    if request.method == 'POST':
        field_name = request.POST.get('field_name')
        new_value = request.POST.get('new_value')
        # print("field_name:", field_name)
        # print("new_value:", new_value)
        # 在这里处理并保存更新后的数据到数据库中
        # 例如：
        administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])

        if field_name == 'administrator_phone':
            # 检查电话是否已经存在
            if new_value != administrator.administrator_phone and models.Administrator.objects.filter(
                    administrator_phone=new_value).exists():
                return JsonResponse({'success': False, 'error_type': 'phone_exists', 'message': 'phone exist'})
            administrator.administrator_phone = new_value
        elif field_name == 'administrator_mail':
            # 检查邮箱是否已经存在
            if new_value != administrator.administrator_mail and models.Administrator.objects.filter(
                    administrator_mail=new_value).exists():
                return JsonResponse({'success': False, 'error_type': 'email_exists', 'message': 'mail exist'})
            administrator.administrator_mail = new_value

        administrator.save()

        return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
    elif request.method == 'GET':
        administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
        context = {
            'administrator_mail': administrator.administrator_mail,
            'administrator_phone': administrator.administrator_phone,

        }
        return render(request, 'app01/ad_account_setting1.html', context)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


# 管理员修改密码
def ad_account_setting1_password(request):
    if request.method == 'POST':
        change_pwd_form = forms.AdministratorChangePwdForm(request.POST)
        if change_pwd_form.is_valid():
            old_password = change_pwd_form.cleaned_data.get('oldPassword')
            new_password = change_pwd_form.cleaned_data.get('newPassword')
            check_password = change_pwd_form.cleaned_data.get('checkPassword')

            print("get form successfully", new_password)

            administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])

            # 进行密码匹配验证
            if new_password != check_password:
                return JsonResponse({'success': False, 'error_type': 'pwdMismatch', 'error': '密码不匹配'})

            if old_password == administrator.administrator_password:
                administrator.administrator_password = new_password
                administrator.save()
                print("save success", new_password)
                return JsonResponse({'success': True, 'message': '密码修改成功'})
            else:
                print("old pwd error")
                return JsonResponse({'success': False, 'error_type': 'old_pwd_error', 'error': '原密码错误'})
        else:
            print("form error")
            return JsonResponse({'success': False, 'error_type': 'invalidForm', 'error': '表单填写不完整或格式不正确'})
    else:
        return render(request, 'app01/ad_account_setting1_password.html')


# 管理员登出
def ad_logout(request):
    django_logout(request)
    request.session.clear()
    return JsonResponse({'success': True})


# 管理员注销
def ad_dispose_account(request):
    administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
    django_logout(request)
    request.session.clear()
    # 注销管理员账户，功能有待调整
    administrator.delete()
    return JsonResponse({'success': True})


# 管理员注册页
def ad_register(request):
    if request.method == 'POST':
        registration_form = forms.AdministratorRegistrationForm(request.POST)
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
            if models.Administrator.objects.filter(administrator_mail=email).exists():
                return JsonResponse({'success': False, 'error_type': 'email_exists', 'error': '该邮箱已被注册'})

            # 检查电话是否已经存在
            if models.Administrator.objects.filter(administrator_phone=phone).exists():
                return JsonResponse({'success': False, 'error_type': 'phone_exists', 'error': '该电话已被注册'})

            # 检查数据库中最大的用户ID
            max_user_id = models.Administrator.objects.latest('administrator_id').administrator_id

            max_user_id = int(max_user_id) if max_user_id else 0
            print("max_user_id:", max_user_id)

            if max_user_id < 9000000:
                new_user_id = 9000001
            else:
                new_user_id = max_user_id + 1
            while models.Administrator.objects.filter(administrator_id=new_user_id).exists():
                new_user_id += 1
            # 自动生成新用户的 id 号

            administrator_register_date = datetime.now()  # 获取注册时间
            try:
                administrator = models.Administrator.objects.create(
                    administrator_id=new_user_id,
                    administrator_name=name,
                    administrator_mail=email,
                    administrator_phone=phone,
                    administrator_register=administrator_register_date,

                    administrator_password=password
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
        return render(request, 'app01/ad_register.html')


# 管理员管理文章页
def ad_manage_article(request):
    # 获取所有文章
    article_list = Article.objects.all().order_by('-article_created')
    # 每页显示 3 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    return render(request, 'app01/ad_manage_article.html', locals())


# 文章删除页
def ad_delete_user_article(request, id):
    # 根据 id 获取需要删除的文章
    article = models.Article.objects.get(article_id=id)
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回个人文章列表
    return redirect("ad_manage_article")


# 管理员管理评论页
def ad_manage_comment(request):
    pass
    return render(request, 'app01/ad_manage_comment.html')


def ad_send_article(request):
    categories = Category.objects.all()
    if request.method == "POST":
        article_post_form = ArticleForm(data=request.POST, files=request.FILES)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            if 'article_image' in request.FILES:
                # 假设 upload_file 是你自定义的处理上传文件的函数
                upload_file(request)

            # 获取当前登录管理员并设置为文章作者
            administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
            new_article.article_adAuthor = administrator

            # 将新文章保存到数据库中
            new_article.save()

            # 保存 tags 的多对多关系
            article_post_form.save_m2m()

            # 处理分类的保存
            selected_categories = article_post_form.cleaned_data.get('categories')
            if selected_categories:
                for category in selected_categories:
                    ArticleCategory.objects.create(article=new_article, category=category)

            return redirect("ad_self_article")
        else:
            print(article_post_form.errors)
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticleForm()

    context = {
        'article_post_form': article_post_form,
        'categories': categories,
    }

    return render(request, 'app01/ad_send_article.html', context)


# 管理员看到的文章详情页
def ad_article_detail(request, id):
    # 取出相应的文章
    article = get_object_or_404(Article, article_id=id)
    # 获取文章的作者
    flag = False
    # 文章作者是管理员
    if article.article_author is None:
        flag = True
        author = article.article_adAuthor
        author_name = article.article_adAuthor.administrator_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_adAuthor=author).count()
        # 获取最新的用户信息
        user = article.article_adAuthor
        user_register_date = user.administrator_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 文章作者是普通用户
    else:
        author = article.article_author
        author_name = article.article_author.user_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_author=author).count()
        # 获取最新的用户信息
        user = article.article_author
        user_register_date = user.user_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 获取按照浏览量排序的文章列表,排除本篇
    top_articles_views = Article.objects.exclude(article_id=id).order_by('-article_views')[:5]
    # 检查是否有热门文章
    if not top_articles_views.exists():
        no_top_articles = True
    else:
        no_top_articles = False
    # 取出文章评论
    comments = Comment.objects.filter(comment_article=article)
    # 浏览量+1
    article.article_views += 1
    article.save(update_fields=['article_views'])
    # 计算评论数量
    article_commentcnt = comments.count()
    article.article_commentcnt = article_commentcnt
    article.save(update_fields=['article_commentcnt'])

    # 字典，内容要传递给模版
    context = {'article': article,
               'author': author,
               'author_name': author_name,
               'post_id': article.article_id,  # 确保 post_id 传递给模板
               'comments': comments,
               'article_commentcnt': article_commentcnt,
               'author_article_count': author_article_count,  # 传递作者文章总数给模板
               'days_diff': days_diff,  # 传递注册天数
               'top_articles_views': top_articles_views,  # 传递热门文章
               'no_top_articles': no_top_articles,
               'flag': flag
               }
    # 载入模板，并返回context对象
    return render(request, 'app01/ad_article.html', context)


# 管理员个人文章列举页
def ad_self_article(request):
    # 获取特定用户
    administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
    # 获取该用户的所有文章
    article_list = models.Article.objects.filter(article_adAuthor=administrator)
    # 每页显示 3 篇文章
    paginator = Paginator(article_list, 3)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    return render(request, 'app01/ad_self_article.html', locals())


# 管理员文章修改页
def ad_update_article(request, id):
    # 获取需要修改的具体文章对象与作者
    article = models.Article.objects.get(article_id=id)
    adAuthor = article.article_adAuthor
    adAuthor_name = article.article_adAuthor.administrator_name
    # 过滤非作者的用户
    if request.session['administrator_id'] != article.article_adAuthor.administrator_id:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = forms.ArticleForm(request.POST, request.FILES)
        # 使用Django内置的方法，判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、content,image,tags 数据并保存
            article.article_title = request.POST['article_title']
            article.article_content = request.POST['article_content']
            if request.FILES.get('article_image'):
                article.article_image = request.FILES.get('article_image')
            # 获取标签字符串
            tag_string = request.POST.get('tags')
            # 分割标签字符串并去除空格，注意是用英文逗号分割
            tags_list = [tag.strip() for tag in tag_string.split(',')]
            # 清除当前文章的所有标签
            article.tags.clear()
            # 设置文章的新标签
            article.tags.add(*tags_list)
            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("ad_article", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = forms.ArticleForm()
        # 赋值上下文
        context = {
            'article': article,
            'id': id,
            'adAuthor_name': adAuthor_name,
            'adAuthor': adAuthor,
            'article_post_form': article_post_form,
        }
        # 返回模板
        return render(request, 'app01/ad_update_article.html', context)


# 管理员文章删除页
def ad_delete_article(request, id):
    # 根据 id 获取需要删除的文章
    article = models.Article.objects.get(article_id=id)
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回个人文章列表
    return redirect("ad_self_article")


# 管理员个人发表的评论列举页
def ad_self_comment(request):
    # 获取特定用户
    administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
    # 获取该用户的所有评论
    comment_list = models.Comment.objects.filter(comment_ad=administrator)
    # 每页显示 5 条评论
    paginator = Paginator(comment_list, 5)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 comments
    comments = paginator.get_page(page)
    return render(request, 'app01/ad_self_comment.html', locals())


# 管理员收到的他人评论列举页
def ad_other_comment(request):
    # 获取特定用户
    administrator = models.Administrator.objects.get(administrator_id=request.session['administrator_id'])
    # 获取该用户收到的所有评论
    comment_list = models.Comment.objects.filter(comment_article__article_adAuthor=administrator)
    # 去除自己给自己的评论
    comment_list = comment_list.exclude(comment_ad=administrator)
    # 每页显示 5 条评论
    paginator = Paginator(comment_list, 5)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 comments
    comments = paginator.get_page(page)
    return render(request, 'app01/ad_other_comment.html', locals())


# 在评论管理页面点击评论跳转并滚动到评论所在位置
def ad_comment_detail(request, article_id, comment_id):
    # 取出相应的文章
    article = get_object_or_404(Article, article_id=article_id)
    # 获取文章的作者
    flag = False
    # 文章作者是管理员
    if article.article_author is None:
        flag = True
        author = article.article_adAuthor
        author_name = article.article_adAuthor.administrator_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_adAuthor=author).count()
        # 获取最新的用户信息
        user = article.article_adAuthor
        user_register_date = user.administrator_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 文章作者是普通用户
    else:
        author = article.article_author
        author_name = article.article_author.user_name
        # 作者文章数
        author_article_count = Article.objects.filter(article_author=author).count()
        # 获取最新的用户信息
        user = article.article_author
        user_register_date = user.user_register  # 假设这是用户注册的日期
        current_date = timezone.now().date()  # 获取当前日期
        days_diff = (current_date - user_register_date).days  # 计算注册到当前的天数
    # 获取按照浏览量排序的文章列表,排除本篇
    top_articles_views = Article.objects.exclude(article_id=article_id).order_by('-article_views')[:5]
    # 检查是否有热门文章
    if not top_articles_views.exists():
        no_top_articles = True
    else:
        no_top_articles = False
    # 取出文章评论
    comments = Comment.objects.filter(comment_article=article)
    # 浏览量+1
    article.article_views += 1
    article.save(update_fields=['article_views'])
    # 计算评论数量
    article_commentcnt = comments.count()
    article.article_commentcnt = article_commentcnt
    article.save(update_fields=['article_commentcnt'])

    # 字典，内容要传递给模版
    context = {'article': article,
               'author': author,
               'author_name': author_name,
               'post_id': article.article_id,  # 确保 post_id 传递给模板
               'comments': comments,
               'comment_id': comment_id,  # comment_id传过去才能滚动定位
               'article_commentcnt': article_commentcnt,
               'author_article_count': author_article_count,  # 传递作者文章总数给模板
               'days_diff': days_diff,  # 传递注册天数
               'top_articles_views': top_articles_views,  # 传递热门文章
               'no_top_articles': no_top_articles,
               'flag': flag,
               }
    # 载入模板，并返回context对象
    return render(request, 'app01/ad_comment_detail.html', context)


# 管理员评论删除页
def ad_delete_comment(request, id):
    # 根据 id 获取需要删除的评论
    comment = models.Comment.objects.get(comment_id=id)
    # 调用.delete()方法删除评论
    comment.delete()
    # 完成删除后返回个人评论列表
    return redirect("ad_self_comment")
