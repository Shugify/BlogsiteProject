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

    # 主页面
    path('home/', views.home, name='home'),
    # 发布博客
    path('send_article/', views.send_article, name='send_article'),
    # 个人博客列举页
    path('my_article/', views.my_article, name='my_article'),
    # 文章修改页
    path('update_article/<str:id>/', views.update_article, name='update_article'),
    # 文章删除页
    path('delete_article/<str:id>/', views.delete_article, name='delete_article'),
    # 个人发表的评论列举页
    path('my_comment/', views.my_comment, name='my_comment'),
    # 收到他人的评论列举页
    path('other_comment/', views.other_comment, name='other_comment'),
    # 在评论管理页面点击评论跳转并滚动到评论所在位置
    path('comment_detail/<str:article_id>/<int:comment_id>/', views.comment_detail, name='comment_detail'),
    # 评论删除页
    path('delete_comment/<str:id>/', views.delete_comment, name='delete_comment'),
    # 文章详情页
    # path('article/<str:id>/', views.article, name='article'),
    path('article/<int:id>/', views.article_detail, name='article'),  # 文章详情
    # 个人信息页
    path('account_setting/', views.account_setting, name='account_setting'),
    # 分类页
    path('category/', views.category, name='category'),
    # 搜索页
    path('search/', views.search_results, name='search_results'),
    # 发布评论页
    path('post_comment/<int:article_id>/', views.post_comment, name='post_comment'),

    # 账户信息页
    path('account_setting1/', views.account_setting1, name='account_setting1'),
    path('account_setting1_password/', views.account_setting1_password, name='account_setting1_password'),
    path('upload_user/', views.upload_user, name='upload_user'),
    path('logout/', views.logout, name='logout'),
    path('dispose_account/', views.dispose_account, name='dispose_account'),

    # 管理员主页,进行用户账户管理
    path('ad_home/', views.ad_home, name='ad_home'),
    # 管理员个人信息页
    path('ad_account_setting/', views.ad_account_setting, name='ad_account_setting'),
    path('upload_administrator/', views.upload_administrator, name='upload_administrator'),
    path('ad_account_setting1/', views.ad_account_setting1, name='ad_account_setting1'),
    path('ad_account_setting1_password/', views.ad_account_setting1_password, name='ad_account_setting1_password'),
    path('ad_logout/', views.ad_logout, name='ad_logout'),
    path('ad_dispose_account/', views.ad_dispose_account, name='ad_dispose_account'),
    path('ad_register/', views.ad_register, name='ad_register'),

    # 管理员文章删除页
    path('ad_delete_user_article/<str:id>/', views.ad_delete_user_article, name='ad_delete_user_article'),
    # 管理员管理文章页
    path('ad_manage_article/', views.ad_manage_article, name='ad_manage_article'),
    # 管理员管理评论页
    path('ad_manage_comment/', views.ad_manage_comment, name='ad_manage_comment'),

    # 管理员发布文章页
    path('ad_send_article/', views.ad_send_article, name='ad_send_article'),
    # 管理员看到的文章详情页（上面一栏导航需要改所以再写一个html）
    path('ad_article/<int:id>/', views.ad_article_detail, name='ad_article'),
    # 管理员发布评论页
    path('ad_post_comment/<int:article_id>/', views.ad_post_comment, name='ad_post_comment'),

    # 管理员个人文章列举页
    path('ad_self_article/', views.ad_self_article, name='ad_self_article'),
    # 管理员修改个人文章页
    path('ad_update_article/<str:id>/', views.ad_update_article, name='ad_update_article'),
    # 管理员删除个人文章页
    path('ad_delete_article/<str:id>/', views.ad_delete_article, name='ad_delete_article'),
    # 管理员个人发表的评论列举页
    path('ad_self_comment/', views.ad_self_comment, name='ad_self_comment'),
    # 管理员收到的他人评论列举页
    path('ad_other_comment/', views.ad_other_comment, name='ad_other_comment'),
    # 在评论管理页面点击评论跳转并滚动到评论所在位置
    path('ad_comment_detail/<str:article_id>/<int:comment_id>/', views.ad_comment_detail, name='ad_comment_detail'),
    # 管理员评论删除页
    path('ad_delete_comment/<str:id>/', views.ad_delete_comment, name='ad_delete_comment'),
    # 用户个人主页按时间顺序展示（普通用户看）
    path('user_detail_lastest/<str:id>/<int:flag>/', views.user_detail_lastest, name='user_detail_lastest'),
    # 用户个人主页按浏览量展示（普通用户看）
    path('user_detail_top/<str:id>/<int:flag>/', views.user_detail_top, name='user_detail_top'),
    # 用户个人主页按时间顺序展示（管理员用户看）
    path('ad_user_detail_lastest/<str:id>/<int:flag>/', views.ad_user_detail_lastest, name='ad_user_detail_lastest'),
    # 用户个人主页按浏览量展示（管理员用户看）
    path('ad_user_detail_top/<str:id>/<int:flag>/', views.ad_user_detail_top, name='ad_user_detail_top'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
