from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    # 登录页
    path('index/', views.user_login, name='index'),
    # 主页面
    path('home/', views.home, name='home'),
    # 发布博客
    path('send_article/', views.send_article, name='send_article'),
    # 个人博客页
    path('my_article/', views.my_article, name='my_article'),
    # 文章详情页
    path('article/', views.article, name='article'),
    # 个人信息页
    path('account_setting/', views.account_setting, name='account_setting'),
    # 分类页
    path('category/', views.category, name='category'),
    # 管理员登录页
    path('ad_login/', views.ad_login, name='ad_login'),
    # 注册页面
    path('register/', views.register, name='register'),
    # 邮箱登录页面
    path('email_login/', views.email_login, name='email_login'),
    # 个人中心页面
    path('self_center/', views.self_center, name='self_center'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
