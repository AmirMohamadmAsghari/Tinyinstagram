from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Like, Images, Dislike, Comment
from user.models import Follow
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse
import logging


def home(request):
    if request.user.is_authenticated:
        user = request.user
        print('user', request.user)
        following_users_ids = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        print('following_users_ids', following_users_ids)
        posts = Post.objects.filter(Q(user=user) | Q(user__id__in=following_users_ids))
        print('posts', posts)
    else:
        posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})


def new_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        images = request.FILES.getlist('photo')
        user_id = request.user.id
        post = Post(content=content,user_id=user_id)
        post.save()
        for image in images:
            image = Images.objects.create(post=post, image=image)
            image.save()
        messages.success(request,'New post created successfully.')
        return redirect('profile')
    return render(request, 'new_post.html')


logger = logging.getLogger(__name__)


def like_post(request):
    logger.debug(f"User {request.user.name} is liking a post")
    if request.method == 'POST':
        user = request.user
        post_id = request.POST.get('post_id')
        if not post_id:
            return JsonResponse({'success': False, 'error': 'Missing post ID'})

        post = get_object_or_404(Post, id=post_id)

        if Like.objects.filter(post=post, user=user).exists():
            Like.objects.get(post=post, user=user).delete()
            liked = False
        else:
            Like.objects.create(post=post, user=user)
            liked = True
            Dislike.objects.filter(post=post, user=user).delete()

        likes_count = post.likes.count()

        return JsonResponse({'success': True, 'liked': liked, 'likes_count': likes_count})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def dislike_post(request):
    logger.debug(f"User {request.user.name} is disliking a post")
    if request.method == 'POST':
        user = request.user
        post_id = request.POST.get('post_id')
        if not post_id:
            return JsonResponse({'success': False, 'error': 'Missing post ID'})

        post = get_object_or_404(Post, id=post_id)

        if Dislike.objects.filter(post=post, user=user).exists():
            Dislike.objects.get(post=post, user=user).delete()
            disliked = False
        else:
            Dislike.objects.create(post=post, user=user)
            disliked = True
            Like.objects.filter(post=post, user=user).delete()

        dislikes_count = post.dislikes.count()

        return JsonResponse({'success': True, 'disliked': disliked, 'dislikes_count': dislikes_count})

    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def add_comment(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment')
        if post_id and comment_text:
            try:
                post = Post.objects.get(id=post_id)
                new_comment = Comment.objects.create(post=post, user=request.user, content=comment_text)
                redirect('home')
            except Post.DoesNotExist:
                # return JsonResponse({'success': False, 'error': 'Post does not exist'})
                pass
        else:
            # return JsonResponse({'success': False, 'error': 'Invalid request parameters'})
            pass
    return redirect('home')


def add_reply(request):
    if request.method == "POST":
        comment_id = request.POST.get('comment_id')
        reply_text = request.POST.get('reply')
        if comment_id and reply_text:
            try:
                parent_comment = Comment.objects.get(id=comment_id)
                new_reply = Comment.objects.create(
                    post=parent_comment.post,
                    user=request.user,
                    content=reply_text,
                    parent_comment=parent_comment
                )
                return redirect('home')
            except Comment.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Parent comment does not exist'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request parameters'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def explore(request):
    posts = Post.objects.all()
    return render(request, 'explorer.html', {'posts': posts})

