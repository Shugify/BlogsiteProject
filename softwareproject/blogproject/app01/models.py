from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from mptt.models import MPTTModel, TreeForeignKey

# Create your models here.
# 自定义表名
# class Meta:
#     db_table = 'Users'


class User(models.Model):  # 用户信息表
    # 用户id，主键
    user_id = models.CharField(max_length=255, primary_key=True, db_index=True)
    # 用户名，默认佚名
    user_name = models.CharField(max_length=255, null=True, default='anonymity')
    # 用户个性签名
    user_introduction = models.CharField(max_length=255, null=True)
    # 用户头像profile photo
    user_pfp = models.ImageField()
    # 用户注册日期
    user_register = models.DateField(null=True)
    # 用户性别，布尔型，0表示女性，1表示男性
    user_sex = models.BooleanField(null=True)
    # 用户年龄
    user_age = models.IntegerField(null=True)
    # 用户生日
    user_birthday = models.DateField(null=True)
    # 用户电话
    user_phone = models.CharField(max_length=255, null=True)
    # 用户邮箱
    user_mail = models.CharField(max_length=255, null=True)
    # 用户ip
    user_ip = models.CharField(max_length=255, null=True)
    # 用户状态，布尔型，0表示用户账号正常，1表示用户已销号（主动/被动）
    user_state = models.BooleanField(null=True)
    # 用户密码
    user_password = models.CharField(max_length=255)


class Administrator(models.Model):  # 管理员信息表
    # 管理员id，主键
    administrator_id = models.CharField(max_length=255, primary_key=True, db_index=True)
    # 管理员名，默认佚名
    administrator_name = models.CharField(max_length=255, null=True, default='anonymity')
    # 管理员个性签名
    administrator_introduction = models.CharField(max_length=255, null=True)
    # 管理员头像profile photo
    administrator_pfp = models.ImageField()
    # 管理员注册日期
    administrator_register = models.DateField(null=True)
    # 管理员性别，布尔型，0表示女性，1表示男性
    administrator_sex = models.BooleanField(null=True)
    # 管理员年龄
    administrator_age = models.IntegerField(null=True)
    # 管理员生日
    administrator_birthday = models.DateField(null=True)
    # 管理员电话
    administrator_phone = models.CharField(max_length=255, null=True)
    # 管理员邮箱
    administrator_mail = models.CharField(max_length=255, null=True)
    # 管理员ip
    administrator_ip = models.CharField(max_length=255, null=True)
    # 管理员密码
    administrator_password = models.CharField(max_length=255)


class Article(models.Model):  # 文章信息表
    # 文章id，主键
    article_id = models.CharField(max_length=255, primary_key=True, db_index=True)
    # 文章作者的id,为User的主键的外键。参数 on_delete 用于指定数据删除的方式。这里设置为空，如果外键那条数据被删除，本条数据就将该字段设置为空。
    article_author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='article')
    # 文章创建时间。参数 default=timezone.now 指定其在创建数据时将默认写入当前的时间
    article_created = models.DateTimeField(default=now)
    # 文章更新时间。参数 auto_now=True 指定每次数据更新时自动写入当前时间
    article_updated = models.DateTimeField(auto_now=True)
    # 文章标题
    article_title = models.CharField(max_length=255)
    # 文章正文。保存大量文本使用 TextField
    article_content = models.TextField()
    # 文章图片
    article_image = models.ImageField()
    # 文章浏览量，默认值=0
    article_views = models.PositiveIntegerField(default=0)
    # 文章评论总数，默认值=0
    article_commentcnt = models.PositiveIntegerField(default=0)
    # 文章点赞量，默认值=0
    # article_likes = models.PositiveIntegerField(default=0)

    # 函数 __str__ 定义当调用对象的 str() 方法时的返回值内容
    def __str__(self):
        # return self.title 将文章标题返回
        return self.article_title

    # 获取文章地址
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.article_id])


class Comment(models.Model):  # 评论信息表
    # 评论id，主键
    comment_id = models.CharField(max_length=255, primary_key=True, db_index=True)
    # 评论所属的文章的id,为Article主键的外键。参数 on_delete 用于指定数据删除的方式。这里设置级联删除，如果外键那条数据被删除，本条数据也删除。
    comment_article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comment')
    # 发表评论的用户的id，为User主键的外键。参数 on_delete 用于指定数据删除的方式。这里设置为空，如果外键那条数据被删除，本条数据就将该字段设置为空。
    comment_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='comment')
    # 评论内容
    comment_content = models.TextField()
    # 评论时间
    comment_created = models.DateTimeField(auto_now_add=True)
    # 评论点赞量，默认值=0
    # comment_likes = models.PositiveIntegerField(default=0)

    # 多级评论，后期加
    # 限制评论最多只能两级，超过两级的评论一律重置为两级，然后再将实际的被评论人存储在reply_to字段中
    # 新增，mptt树形结构
    # parent = TreeForeignKey(
    #     'self',
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name='children'
    # )

    # 新增，记录二级评论回复给谁, str
    # reply_to = models.ForeignKey(
    #     User,
    #     null=True,
    #     blank=True,
    #     on_delete=models.CASCADE,
    #     related_name='repliers'
    # )

    # 替换 Meta 为 MPTTMeta
    class Meta:
        ordering = ('comment_created',)
    # class MPTTMeta:
    #     order_insertion_by = ['created']

    def __str__(self):
        return self.comment_content[:20]


class Category(models.Model):  # 分类信息表
    # 分类id,主键
    category_id = models.CharField(max_length=255, primary_key=True, db_index=True)
    # 分类名
    category_name = models.CharField(max_length=255, null=True)
    # 分类描述
    category_description = models.TextField()
    # 分类创建时间
    category_created = models.DateTimeField(default=now)


class ArticleCategory(models.Model):  # 文章设置分类表
    # 关系：多对多
    article_id = models.CharField(max_length=255)
    category_id = models.CharField(max_length=255)
    # Django只能定义一个primary_key=True
    # 通过unique_together定义复合主键

    class Meta:
        unique_together = [['article_id', 'category_id']]
