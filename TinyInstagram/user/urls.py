from django.urls import path
from . import views

urlpatterns = [
    path('', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('logout/', views.logout_user, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('user_profile/<int:user_id>/', views.user_profile, name='user_profile'),
    # path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('search/', views.search_user, name='search_user'),
    path('follow/<int:profile_id>/<action>/', views.follow_user, name='follow_user'),
    # path('unfollow/<int:profile_id>/', views.unfollow_user, name='unfollow_user_ajax'),
]

