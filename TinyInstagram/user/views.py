from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import FollowSerializer
from django.shortcuts import render, redirect
from .models import User, Profile, Follow
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from .utils import generate_otp_code, send_email


def check_username(request):
    username = request.POST.get('name')
    print(username)
    user_exists = User.objects.filter(name=username).exists()
    return JsonResponse({'exists': user_exists})


def check_email(request):
    email = request.POST.get('email')
    # You can use a library like validate_email to check email format
    # Here, we assume a basic format validation
    is_valid = '@' in email and '.' in email
    email_exists = User.objects.filter(email=email).exists()
    return JsonResponse({'valid': is_valid, 'exists': email_exists})


def check_phone(request):
    phone = request.POST.get('phone')
    phone_exists = User.objects.filter(phone=phone).exists()
    return JsonResponse({'exists': phone_exists})
# Create your views here.


def register(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        hashed_password = make_password(password)
        user = User(name=name, email=email, phone=phone, password=hashed_password)
        user.save()
        messages.success(request, 'user registered successfully!', 'success')
        profile = Profile(user_id=user.id, followers=0, following=0, avatar=None, bio="")
        profile.save()
        return redirect('home')

    return render(request, 'register.html')


def login_user(request):
    if request.method == 'GET' and request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        if not (phone and password):
            messages.error(request, 'Please provide both phone and password.')
            return redirect('login')

        user = authenticate(request, phone=phone, password=password)
        if user is not None:

            otp_code = generate_otp_code()

            user.otp_code = otp_code
            user.save()

            send_email(user.email, otp_code)

            return redirect('verify_otp')
        else:
            messages.error(request, 'The phone number or password is incorrect. Please try again.')
            return redirect('login')

    return render(request, 'login.html')


def verify_otp(request):
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        phone = request.POST.get('phone')
        print(phone, otp_code)
        user = User.objects.filter(phone=phone).first()
        if user:
            print(user.phone, user.otp_code)
            if str(user.otp_code).strip() == str(otp_code).strip():
                login(request, user)
                messages.success(request, 'Your login was successful!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid OTP code.')
        else:
            messages.error(request, 'User does not exist.')
        return redirect('login')
    return render(request, 'otp_verification.html')


def logout_user(request):
    logout(request)
    messages.success(request, 'logged out successfully!', 'success')
    return redirect('login')


@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'profile.html', {"profile": profile})


def profile_edit(request):
    if request.method == 'POST':
        profile = request.user.profile
        bio = request.POST.get('bio')
        avatar = request.FILES.get('avatar')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.', 'error')
            return redirect('profile_edit')

        if avatar:
            profile.avatar = avatar
        profile.bio = bio
        profile.save()

        if new_password:
            request.user.password = make_password(new_password)
            request.user.save()
            messages.success(request, 'Your password was successfully updated.', 'success')

        messages.success(request, 'Your changes have been saved.', 'success')
        return redirect('profile')
    return render(request, 'profile_edit.html')


def user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(Profile, user=user)

    return render(request, 'user_profile.html', {"user": user, 'profile': profile})


# @login_required
# def follow_user(request, user_id):
#     if request.method == 'POST' and request.is_ajax():
#         # Check if the user exists and is not the same as the logged-in user
#         try:
#             user_to_follow = User.objects.get(id=user_id)
#             if user_to_follow == request.user:
#                 return JsonResponse({'success': False, 'error': 'You cannot follow yourself'})
#         except User.DoesNotExist:
#             return JsonResponse({'success': False, 'error': 'User does not exist'})
#
#         # Check if the user is already being followed
#         if not Follow.objects.filter(follower=request.user, following=user_to_follow).exists():
#             # If not, create a new Follow object
#             Follow.objects.create(follower=request.user, following=user_to_follow)
#             # Update follower count for both users
#             request.user.profile.following += 1
#             request.user.profile.save()
#             user_to_follow.profile.followers += 1
#             user_to_follow.profile.save()
#             return JsonResponse({'success': True})
#         else:
#             return JsonResponse({'success': False, 'error': 'You are already following this user'})
#     else:
#         return JsonResponse({'success': False, 'error': 'Invalid request method'})
@api_view(['POST'])
@login_required
def follow_user(request, profile_id, action):
    if action == 'follow':
        if request.method == 'POST':
            profile = get_object_or_404(Profile, id=profile_id)
            follower_profile = request.user.profile
            follow_instance, create = Follow.objects.get_or_create(follower=follower_profile, following=profile.user)
            if create:
                profile.followers += 1
                profile.save()
                follower_profile.following += 1
                follower_profile.save()
                follow_serializer = FollowSerializer(follow_instance)
                return Response({'status': 'success', 'action': 'followed', 'following_count': profile.followers, 'follow': follow_serializer.data})
            else:
                return Response({'status': 'error', 'message': 'You are already following this user.'}, status=400)
    elif action == 'unfollow':
        if request.method == 'POST':
            profile = get_object_or_404(Profile, pk=profile_id)
            follower_profile = request.user.profile
            follow_instance = Follow.objects.filter(follower=follower_profile.user, following=profile.user).first()
            if follow_instance:
                follow_instance.delete()
                profile.followers -= 1
                profile.save()
                follower_profile.following -= 1
                follower_profile.save()
                return Response({'status': 'success', 'action': 'unfollowed', 'following_count': profile.followers})
            else:
                return Response({'status': 'error', 'message': 'You are not following this user.'}, status=400)

        return Response({'status': 'error', 'message': 'Invalid action or request method.'}, status=400)


# @login_required
# def follow_user(request, profile_id, action):
#     if action == 'follow':
#         if request.method == 'POST':
#             profile = get_object_or_404(Profile, pk=profile_id)
#             follower_profile = request.user.profile
#             follow_instance, created = Follow.objects.get_or_create(follower=follower_profile.user,
#                                                                     following=profile.user)
#             if created:
#                 profile.followers += 1
#                 profile.save()
#                 follower_profile.following += 1
#                 follower_profile.save()
#                 return JsonResponse({'status': 'success', 'action': 'followed', 'following_count': profile.followers})
#             else:
#                 return JsonResponse({'status': 'error', 'message': 'You are already following this user.'})
#     elif action == 'unfollow':
#         if request.method == 'POST':
#             profile = get_object_or_404(Profile, pk=profile_id)
#             follower_profile = request.user.profile
#             follow_instance = Follow.objects.filter(follower=follower_profile.user, following=profile.user).first()
#             if follow_instance:
#                 follow_instance.delete()
#                 profile.followers -= 1
#                 profile.save()
#                 follower_profile.following -= 1
#                 follower_profile.save()
#                 return JsonResponse({'status': 'success', 'action': 'unfollowed', 'following_count': profile.followers})
#             else:
#                 return JsonResponse({'status': 'error', 'message': 'You are not following this user.'})
#
#     return JsonResponse({'status': 'error', 'message': 'Invalid action or request method.'}, status=400)


# @login_required
# def unfollow_user(request, profile_id):
#     if request.method == 'POST':
#         profile = get_object_or_404(Profile, pk=profile_id)
#         follower = request.user.profile
#         follow_instance = Follow.objects.filter(follower=follower, following=profile.user).first()
#         if follow_instance:
#             follow_instance.delete()
#             profile.followers -= 1
#             profile.save()
#             return JsonResponse({'status': 'success', 'action': 'unfollowed'})
#         else:
#             return JsonResponse({'status': 'error', 'message': 'You are not following this user.'})


def search_user(request):
    query = request.GET.get('query', '')
    if query:
        results = User.objects.filter(name__icontains=query)[:10]
        if results:

            search_results = [{'id': user.id, 'name': user.name} for user in results]
            return JsonResponse(search_results, safe=False)
        else:
            return JsonResponse({'message': 'User not found'})
    else:
        return JsonResponse({'message': 'Enter a search query.'})
