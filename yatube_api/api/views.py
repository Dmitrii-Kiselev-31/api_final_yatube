from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .permissions import IsAuthorOrReadOnly
from posts.models import Group, Post, User, Comment
from .serializers import (
    GroupSerializer, PostSerializer, CommentSerializer, FollowSerializer
)

API_403 = PermissionDenied('Изменение чужого контента запрещено!') 

class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise API_403
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise API_403
        instance.delete()


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly
    ]

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return post.comments.select_related('author')
 
    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        serializer.save(author=self.request.user, post=post)

    def perform_update(self, serializer):
        if serializer.instance.author != self.request.user:
            raise API_403
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        if instance.author != self.request.user:
            raise API_403
        instance.delete()


class FollowViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__username']

    def get_queryset(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return user.follower

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)