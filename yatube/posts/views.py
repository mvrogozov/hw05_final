from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, ListView, UpdateView

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


class IndexView(ListView):

    model = Post

    paginate_by = settings.POSTS_AMOUNT

    template_name = 'posts/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        title = "Последние обновления на сайте"
        context.update({
            'title': title
        }
        )
        return context


class GroupView(ListView):
    paginate_by = settings.POSTS_AMOUNT
    template_name = 'posts/group_list.html'

    def get_queryset(self):
        self.group = get_object_or_404(Group, slug=self.kwargs['slug'])
        self.posts_list = self.group.posts.select_related('author')
        return self.posts_list

    def get_context_data(self, **kwargs):
        context = super(GroupView, self).get_context_data(**kwargs)
        title = f'Записи сообщества {self.group.title}'
        context.update({
            'title': title,
            'group': self.group
        }
        )
        return context


class ProfileView(ListView):
    template_name = 'posts/profile.html'
    paginate_by = settings.POSTS_AMOUNT

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        self.posts_list = Post.objects.select_related(
            'group', 'author'
        ).filter(
            author=self.user
        )
        return self.posts_list

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        if Follow.objects.filter(
            user=self.request.user, author=self.user
        ).exists():
            following = True
        else:
            following = False
        title = 'Профайл пользователя ' + self.kwargs['username']
        context.update({
            'title': title,
            'author': self.user,
            'following': following
        }
        )
        return context


class PostDetailView(ListView):
    template_name = 'posts/post_detail.html'

    def get_queryset(self):
        self.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        self.comments_list = Comment.objects.select_related('author').filter(
            post=self.kwargs['post_id']
        )
        return self.comments_list

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        title = self.post.text[:30]
        form = CommentForm()
        posts_total = Post.objects.filter(author=self.post.author).count()
        context.update({
            'post': self.post,
            'posts_total': posts_total,
            'title': title,
            'form': form,
        }
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    template_name = 'posts/create_post.html'
    form_class = PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return redirect('posts:profile', self.request.user)

    def get_context_data(self, **kwargs):
        context = super(PostCreateView, self).get_context_data(**kwargs)
        context.update({
            'is_edit': False,
        }
        )
        return context


class PostEditView(LoginRequiredMixin, UpdateView):
    template_name = 'posts/create_post.html'
    model = Post
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        """ Making sure that only authors can update stories """
        obj = self.get_object()
        if obj.author != self.request.user:
            return redirect('posts:post_detail', obj.pk)
        return super(PostEditView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return redirect('posts:post_detail', self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super(PostEditView, self).get_context_data(**kwargs)
        context.update({
            'is_edit': True,
        }
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    template_name = 'posts/includes/add_comment.html'
    form_class = CommentForm

    def get(self, request, *args, **kwargs):
        return redirect('posts:post_detail', post_id=kwargs['post_id'])

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.post = post
        comment.save()
        return redirect('posts:post_detail', post_id=post.pk)


class FollowIndexView(LoginRequiredMixin, ListView):
    template_name = 'posts/follow.html'
    model = Post
    paginate_by = settings.POSTS_AMOUNT

    def get_queryset(self):
        authors_list = Follow.objects.filter(
            user=self.request.user
        ).values_list('author')
        authors_id_list = [a[0] for a in authors_list]
        posts_list = Post.objects.select_related(
            'author'
        ).filter(author__in=authors_id_list)
        return posts_list


class ProfileFollowView(LoginRequiredMixin, UpdateView):
    template_name = 'posts/follow.html'
    model = Follow

    def get(self, *args, **kwargs):
        selected_author = User.objects.get(username=self.kwargs['username'])
        if selected_author == self.request.user:
            return redirect('/')    
        obj, created = Follow.objects.get_or_create(user=self.request.user)
        obj.author.add(selected_author)
        return redirect('/')


class ProfileUnfollowView(LoginRequiredMixin, UpdateView):
    model = Follow

    def get(self, *args, **kwargs):
        selected_author = User.objects.get(username=self.kwargs['username'])
        obj = get_object_or_404(Follow, user=self.request.user)
        obj.author.remove(selected_author)
        return redirect('/')
