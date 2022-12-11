from django import forms

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


class RegisterForm(forms.Form):
    username = forms.CharField(label='User nae', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入账号'}))
    password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码','id': 'ipwd'}))
    duplicate = forms.BooleanField(label='Duplicate username', required=False)
    #password1 = forms.CharField(label='Password1', max_length=100)
    success = forms.BooleanField(label='Register successfully', required=False)


class LoginForm(forms.Form):
    username = forms.CharField(label='账号', max_length=100)
    password = forms.CharField(label='密码', max_length=100, widget=forms.PasswordInput())
    error = forms.BooleanField(label='Error', required=False)


class SearchForm(forms.Form):
    key = forms.CharField(label='search key', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'search'}))
    
