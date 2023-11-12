from django import forms
from .models import Post, Comment
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.auth.forms import UserChangeForm

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['title', 'text', 'location', 'category', 'pub_date']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-input'}),
        }


class EditForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email')


class CommentForm(forms.ModelForm):
    
    class Meta:
        model = Comment
        fields = ('text',)