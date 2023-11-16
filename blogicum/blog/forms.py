from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm

from .models import Comment, Post


User = get_user_model()


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        exclude = ['author']
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class EditForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email'
        )


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
