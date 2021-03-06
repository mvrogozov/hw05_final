from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.decorators.cache import cache_page

from . import views

app_name = 'posts'

urlpatterns = [
    path(
        '',
        cache_page(20)(views.IndexView.as_view()),
        name='index'
    ),

    path(
        'group/<slug:slug>/',
        views.GroupView.as_view(),
        name='group_list'
    ),
    path(
        'profile/<str:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='post_create'
    ),
    path(
        'posts/<int:post_id>/edit/',
        login_required(views.PostEditView.as_view()),
        name='post_edit'
    ),
    path(
        'posts/<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/follow/',
        views.FollowIndexView.as_view(),
        name='follow_index'
    ),

    path(
        'follow/',
        views.FollowIndexView.as_view(),
        name='follow_index'
    ),

    path(
        'profile/<str:username>/follow/',
        views.ProfileFollowView.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnfollowView.as_view(),
        name='profile_unfollow'
    ),
]
