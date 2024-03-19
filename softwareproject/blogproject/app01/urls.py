from django.urls import path
from . import views
urlpatterns = [
    # 首页
    path('', views.index, name='index'),
    # 登录页
    path('login/', views.login, name='login'),
    # 主页面
    path('index/', views.index, name='index'),
    # 个人博客页
    path('my_article/', views.my_article, name='my_article'),
    # 文章详情页
    path('article/', views.article, name='article'),
    # 个人信息页
    path('account_setting/', views.account_setting, name='account_setting'),
    # 分类页
    path('category/', views.category, name='category'),
]
