from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm, UserUpdateForm, PostForm
from .models import Post

User = get_user_model()



class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('login')



def user_profile(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    user_posts = user_obj.posts.all().order_by('-created_at')

    context = {
        'user_obj': user_obj,
        'user_posts': user_posts,
    }
    return render(request, 'users/user_profile.html', context)



@login_required(login_url='login')
def profile_edit(request):
    user = request.user

    if request.method == 'POST':
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.pk)
    else:
        form = UserUpdateForm(instance=user)

    return render(request, 'users/profile_edit.html', {'form': form, 'title': 'Profilni tahrirlash'})



def post_list(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts/post_list.html', {'posts': posts})



@login_required(login_url='login')  # LOGIN TALAB QILINADI
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    # Login qilgani aniq bo'lgani uchun faqat mualliflikni tekshiramiz
    can_edit = request.user == post.author

    context = {
        'post': post,
        'can_edit': can_edit
    }
    return render(request, 'posts/post_detail.html', context)



@login_required(login_url='login')
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()

    return render(request, 'posts/post_form.html', {'form': form, 'title': 'Yangi Post'})



@login_required(login_url='login')
def post_update(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        return redirect('post_detail', pk=post.pk)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'posts/post_form.html', {'form': form, 'title': 'Postni tahrirlash'})



@login_required(login_url='login')
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author:
        return redirect('post_detail', pk=post.pk)

    if request.method == 'POST':
        post.delete()
        return redirect('post_list')

    return render(request, 'posts/post_confirm_delete.html', {'post': post})