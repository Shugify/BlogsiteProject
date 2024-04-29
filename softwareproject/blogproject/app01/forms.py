# 引入表单类
from django import forms
# 引入文章模型
from .models import Article
from .models import Comment
# 引入 User 模型
from django.contrib.auth.models import User


# 写文章的表单类
class ArticleForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = Article
        # 定义表单包含的字段
        fields = ('article_title', 'article_content', 'article_image', 'tags')


class UserLoginForm(forms.Form):
    uid = forms.CharField(label='User ID', max_length=100, required=True)
    pwd = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput, required=True)


class UserRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, label='姓名')
    email = forms.EmailField(label='邮箱')
    phone = forms.CharField(max_length=20, label='电话')
    password = forms.CharField(widget=forms.PasswordInput, label='密码')
    rpassword = forms.CharField(widget=forms.PasswordInput, label='确认密码')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        rpassword = cleaned_data.get('rpassword')

        # 确认密码匹配验证
        if password and rpassword and password != rpassword:
            raise forms.ValidationError("密码不匹配，请重新输入。")

        return cleaned_data


class UserEmailLoginForm(forms.Form):
    email = forms.CharField(label='Email')
    pwd = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput, required=True)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment_content']


class UserChangePwdForm(forms.Form):
    oldPassword = forms.CharField(widget=forms.PasswordInput, label='原密码')
    newPassword = forms.CharField(widget=forms.PasswordInput, label='新密码')
    checkPassword = forms.CharField(widget=forms.PasswordInput, label='确认密码')




class ADLoginForm(forms.Form):
    aid = forms.CharField(label='AD ID', max_length=100, required=True)
    pwd = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput, required=True)

class AdministratorChangePwdForm(forms.Form):
    oldPassword = forms.CharField(widget=forms.PasswordInput, label='原密码')
    newPassword = forms.CharField(widget=forms.PasswordInput, label='新密码')
    checkPassword = forms.CharField(widget=forms.PasswordInput, label='确认密码')


class AdministratorRegistrationForm(forms.Form):
    name = forms.CharField(max_length=100, label='姓名')
    email = forms.EmailField(label='邮箱')
    phone = forms.CharField(max_length=20, label='电话')
    password = forms.CharField(widget=forms.PasswordInput, label='密码')
    rpassword = forms.CharField(widget=forms.PasswordInput, label='确认密码')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        rpassword = cleaned_data.get('rpassword')

        # 确认密码匹配验证
        if password and rpassword and password != rpassword:
            raise forms.ValidationError("密码不匹配，请重新输入。")

        return cleaned_data
