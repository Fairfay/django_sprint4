from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from django.db.models import Count

from blog.models import Post


User = get_user_model()

NUM_POSTS_TO_DISPLAY = 10


def get_published_posts():
    return Post.objects.select_related(
        'author', 'location', 'category'
    ).filter(
        pub_date__lte=timezone.now(),
        category__is_published=True,
        is_published=True,
    )


def get_paginated_posts(request, posts):
    paginator = Paginator(posts.order_by('-pub_date')
                          .annotate(comment_count=Count("comments")),
                          NUM_POSTS_TO_DISPLAY)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    return page_obj
