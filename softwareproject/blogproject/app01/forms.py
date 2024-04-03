# 引入表单类
from django import forms
# 引入 User 模型
from django.contrib.auth.models import User


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
