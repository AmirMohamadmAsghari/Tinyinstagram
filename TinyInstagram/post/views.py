from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import LikeSerializer, DislikeSerializer
from .models import Post, Like, Images, Dislike, Comment
from user.models import Follow
from django.db.models import Q
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
import logging
from django.contrib.auth.decorators import login_required


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

@api_view(['POST'])
def like_post(request):
    if request.method == 'POST':
        user = request.user
        post_id = request.data.get('post_id')
        if not post_id:
            return Response({'success' : False, 'error' : 'Missing post ID'}, status=400)
        post = get_object_or_404(Post, pk=post_id)
        like_exists = Like.objects.filter(post=post, user=user).exists()
        if like_exists:
            like_instance = Like.objects.get(post=post, user=user)
            like_instance.delete()
            liked = False
        else:
            Like.objects.create(post=post, user=user)
            liked = True
            Dislike.objects.filter(post=post, user=user).delete()

        likes_count = post.likes.count()

        like_serializer = LikeSerializer(like_instance if like_exists else None)
        likes_data = like_serializer.data if like_exists else None
        return Response({'success':True, 'liked':liked, 'likes_count':likes_count,'like':likes_data})
    else:
        return Response({'success': False, 'error': 'Invalid request method'}, status=405)


# def like_post(request):
#     logger.debug(f"User {request.user.name} is liking a post")
#     if request.method == 'POST':
#         user = request.user
#         post_id = request.POST.get('post_id')
#         if not post_id:
#             return JsonResponse({'success': False, 'error': 'Missing post ID'})
#
#         post = get_object_or_404(Post, id=post_id)
#
#         if Like.objects.filter(post=post, user=user).exists():
#             Like.objects.get(post=post, user=user).delete()
#             liked = False
#         else:
#             Like.objects.create(post=post, user=user)
#             liked = True
#             Dislike.objects.filter(post=post, user=user).delete()
#
#         likes_count = post.likes.count()
#
#         return JsonResponse({'success': True, 'liked': liked, 'likes_count': likes_count})
#
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})


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
        referring_page = request.POST.get('referring_page')
        print("Referring Page:", referring_page)
        if post_id and comment_text:
            try:
                post = Post.objects.get(id=post_id)
                new_comment = Comment.objects.create(post=post, user=request.user, content=comment_text)
                if referring_page == 'explore':
                    return redirect('explore')
                elif referring_page == 'home':
                    return redirect('home')
                else:
                    # Handle the case where referring_page is not recognized
                    pass
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
        referring_page = request.POST.get('referring_page')
        print("Referring Page:", referring_page)
        if comment_id and reply_text:
            try:
                parent_comment = Comment.objects.get(id=comment_id)
                new_reply = Comment.objects.create(
                    post=parent_comment.post,
                    user=request.user,
                    content=reply_text,
                    parent_comment=parent_comment
                )
                if referring_page == 'explore':
                    return HttpResponseRedirect(reverse('explore'))
                elif referring_page == 'home':
                    return HttpResponseRedirect(reverse('home'))
                else:
                    # Handle the case where referring_page is not recognized
                    pass
            except Comment.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Parent comment does not exist'})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid request parameters'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})


def explore(request):
    posts = Post.objects.all()
    return render(request, 'explorer.html', {'posts': posts})


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user:
        comment.delete()
    referring_page = request.POST.get('referring_page', 'home')
    if referring_page == 'explore':
        return redirect('explore')
    else:
        return redirect('home')
