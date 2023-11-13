from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.utils import timezone

from django.db.models import Count

from django.http import HttpResponse

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from blog.models import Post, Category, Comment

from .forms import PostForm, EditForm, CommentForm


User = get_user_model()

NUM_POSTS_TO_DISPLAY = 10


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')


def get_published_posts():
    return Post.objects.select_related(
        'author', 'location'
    ).filter(
        pub_date__lte=timezone.now(),
        category__is_published=True,
        is_published=True,
    )

# Не понимаю как обойти тесты для использования функции


def get_unpublished_posts():
    return Post.objects.select_related(
        'author', 'location'
    ).filter(
        pub_date__lte=timezone.now(),
        category__is_published=True,
    )


def index(request):
    posts = get_published_posts().order_by('-created_at').annotate(
        comment_count=Count("comment"))
    paginator = Paginator(posts, NUM_POSTS_TO_DISPLAY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'blog/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, id):
    form = CommentForm()
    post = get_object_or_404(Post.objects.select_related('author', 'location'),
                             pk=id)
    if request.user != post.author:
        posts = Post.objects.select_related('author', 'location').filter(
            is_published=True,
            category__is_published=True
        )
        post = get_object_or_404(posts, pk=id)
        comments = post.comment.all()
        return render(request, 'blog/detail.html', {'post': post, 'form': form,
                                                    'comments': comments})
    else:
        comments = post.comment.all()
        return render(request, 'blog/detail.html', {'post': post, 'form': form,
                                                    'comments': comments})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = category.posts.all().select_related(
        'location',
        'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now()
    )
    paginator = Paginator(posts, NUM_POSTS_TO_DISPLAY)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
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
    template = 'blog/create.html'
    context = {'form': form}
    return render(request, template, context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts_query = profile.posts.all()
    if request.user != profile:
        posts_query = posts_query.filter(is_published=True)
    posts_query = posts_query.order_by('-created_at').annotate(
        comment_count=Count("comment"))
    paginator = Paginator(posts_query, NUM_POSTS_TO_DISPLAY)
    page_obj = paginator.get_page(request.GET.get('page'))
    template = 'blog/profile.html'
    context = {
        'page_obj': page_obj,
        'profile': profile,
    }
    return render(request, template, context)


@login_required
def edit_profile(request, username):
    profile = get_object_or_404(User, username=username)
    if request.method == 'POST':
        form = EditForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username)
    else:
        form = EditForm(instance=profile)
    template = 'blog/user.html'
    context = {'form': form, 'profile': profile, 'is_edit': True}
    return render(request, template, context)


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
    template = 'blog/create.html'
    context = {'form': form, 'post': post, 'is_edit': True}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:index')
    template = 'blog/create.html'
    context = {'post': post}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', id=post_id) 


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    form = CommentForm(
        request.POST or None,
        files=request.FILES or None,
        instance=comment)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', post_id)
    template = 'blog/comment.html'
    context = {'form': form, 'comment': comment, 'is_edit': True}
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id)
    template = 'blog/comment.html'
    context = {'comment': comment}
    return render(request, template, context)
