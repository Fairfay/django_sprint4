from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect

from blog.forms import CommentForm, EditForm, PostForm
from blog.models import Category, Comment, Post
from blog.utils import get_published_posts, get_paginated_posts


User = get_user_model()

NUM_POSTS_TO_DISPLAY = 10


def index(request):
    published_posts = get_published_posts()
    page_obj = get_paginated_posts(request, published_posts)
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    form = CommentForm()
    post = get_object_or_404(Post.objects.select_related('author', 'location',
                                                         'category'),
                             pk=id)
    if request.user != post.author:
        posts = get_published_posts()
        post = get_object_or_404(posts, pk=id)
        comments = post.comments.all()
        return render(request, 'blog/detail.html', {'post': post, 'form': form,
                                                    'comments': comments})
    comments = post.comments.all()
    return render(request, 'blog/detail.html', {'post': post, 'form': form,
                                                'comments': comments})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = get_published_posts().filter(
        category=category,
    ).select_related(
        'location',
        'author',
        'category'
    )
    page_obj = get_paginated_posts(request, posts)
    return render(request, 'blog/category.html', {'category': category,
                                                  'page_obj': page_obj})


@login_required
def create_post(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        create_post = form.save(commit=False)
        create_post.author = request.user
        create_post.save()
        return redirect('blog:profile', create_post.author)
    return render(request, 'blog/create.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts_query = profile.posts.all()
    if request.user != profile:
        posts_query = get_published_posts()
    page_obj = get_paginated_posts(request, posts_query)
    return render(request, 'blog/profile.html', {
        'page_obj': page_obj,
        'profile': profile,
    })


@login_required
def edit_profile(request):
    profile = get_object_or_404(User, username=request.user.username)
    form = EditForm(request.POST or None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=profile.username)
    return render(request, 'blog/user.html', {'form': form,
                                              'profile': profile})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/create.html',
                  {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    return render(request, 'blog/create.html', {'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comments = form.save(commit=False)
        comments.author = request.user
        comments.post = post
        comments.save()
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comments = get_object_or_404(Comment, id=comment_id)
    if request.user != comments.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None,
        instance=comments)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html',
                  {'form': form, 'comment': comments})


@login_required
def delete_comment(request, post_id, comment_id):
    comments = get_object_or_404(Comment, id=comment_id)
    if request.user != comments.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comments.delete()
        return redirect('blog:post_detail', post_id)
    return render(request, 'blog/comment.html', {'comment': comments})
