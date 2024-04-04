from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    # 用户登录页
    path('index/', views.user_login, name='index'),
    # 管理员登录页
    path('ad_login/', views.ad_login, name='ad_login'),
    # 注册页面
    path('register/', views.register, name='register'),
    # 邮箱登录页面
    path('email_login/', views.email_login, name='email_login'),
    # 个人中心页面
    path('self_center/', views.self_center, name='self_center'),
    # 主页面
    path('home/', views.home, name='home'),
    # 发布博客
    path('send_article/', views.send_article, name='send_article'),
    # 个人博客页
    path('my_article/', views.my_article, name='my_article'),
    # 文章修改页
    path('update_article/<str:id>/', views.update_article, name='update_article'),
    # 文章删除页
    path('delete_article/<str:id>/', views.delete_article, name='delete_article'),
    # 个人评论列举页
    path('my_comment/', views.my_comment, name='my_comment'),
    # 他人评论列举页
    path('other_comment/', views.other_comment, name='other_comment'),
    # 评论删除页
    path('delete_comment/<str:id>/', views.delete_comment, name='delete_comment'),
    # 文章详情页
    path('article/<str:id>/', views.article, name='article'),
    # 个人信息页
    path('account_setting/', views.account_setting, name='account_setting'),
    # 分类页
    path('category/', views.category, name='category'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
