from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.paginator import Paginator
from blog.models import Post, Category, Comment
from django.contrib.auth.decorators import login_required
from .forms import PostForm, EditForm, CommentForm
from django.contrib.auth.forms import UserChangeForm


User = get_user_model()

NUM_POSTS_TO_DISPLAY = 10


def get_published_posts():
    return Post.objects.select_related(
        'author', 'location'
    ).filter(
        is_published=True,
        #pub_date__lte=timezone.now(),
        category__is_published=True
    )



def index(request):
    paginator = Paginator(
        Post.objects.all(),
        NUM_POSTS_TO_DISPLAY
    )
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'blog/index.html'
    context = {
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, id):
    posts = get_published_posts()
    post = get_object_or_404(posts, pk=id)
    return render(request, 'blog/detail.html', {'post': post})


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
    return render(request, 'blog/category.html',
                  {'category': category, 'post_list': posts})


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
    paginator = Paginator(
        profile.posts.all(),
        NUM_POSTS_TO_DISPLAY
    )
    page_obj = paginator.get_page(
        request.GET.get('page')
    )
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
    template = 'blog/create_post.html'
    context = {'form': form, 'post': post, 'is_edit': True}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id)
    if request.method == 'POST':
        post.delete()
        return redirect('blog:post_detail')
    template = 'blog/create.html'
    context = {'post': post}
    return render(request, template, context)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk) 