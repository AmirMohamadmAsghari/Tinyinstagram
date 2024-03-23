from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('new_post/', views.new_post, name='new_post'),
    path('like_post/', views.like_post, name='like_post'),
    path('dislike-post/', views.dislike_post, name='dislike_post'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('add_reply/', views.add_reply, name='add_reply'),
    path('explore/', views.explore, name='explore'),

]
