from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GroupViewSet, PostViewSet, CommentViewSet, FollowViewSet

router = DefaultRouter()

router.register('groups', GroupViewSet, basename='groups')
router.register('posts', PostViewSet, basename='posts')
router.register(
    r'posts/(?P<post_id>\d+)/comments', CommentViewSet, basename='comments'
)
router.register('follow', FollowViewSet, basename='follow')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.jwt')),
]
