from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Post, PostImage, Profile, Comment
from .forms import UserRegisterForm, PostForm, ImageForm, ImageFormSet, ProfileForm, modelformset_factory
from django.contrib import messages
from django.db.models import Q
from django.contrib.postgres.search import TrigramSimilarity
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json



def home(request):
    query = request.GET.get('q', '')
    if query:
        posts = Post.objects.annotate(
            title_similarity=TrigramSimilarity('title', query),
            location_similarity=TrigramSimilarity('location', query),
        ).filter(
            Q(title_similarity__gte=0.3) | Q(location_similarity__gte=0.3)
        ).order_by('-title_similarity', '-location_similarity')
    else:
        posts = Post.objects.prefetch_related(
            'images', 'comments__replies'
        ).order_by('-created_at')

    return render(request, 'gobuybro/home.html', {'posts': posts})


@csrf_exempt
def add_comment(request, post_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text')
            parent_id = data.get('parent_id')
            post = Post.objects.get(id=post_id)

            if not text:
                return JsonResponse({"status": "error", "message": "Comment cannot be empty."})

            if parent_id:
                parent = Comment.objects.get(id=parent_id)
                comment = Comment.objects.create(user=request.user, post=post, text=text, parent=parent)
            else:
                comment = Comment.objects.create(user=request.user, post=post, text=text)

            return JsonResponse({
                "status": "success",
                "comment": {
                    "id": comment.id,
                    "text": comment.text,
                    "username": comment.user.username,
                    "parent_id": comment.parent.id if comment.parent else None,
                }
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "Invalid request"})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'gobuybro/register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    return render(request, 'gobuybro/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def post_create(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        image_formset = ImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.none())
        
        if post_form.is_valid() and image_formset.is_valid():
            post = post_form.save(commit=False)
            post.owner = request.user  # Assuming the user must be logged in
            post.save()
            
            for form in image_formset.cleaned_data:
                if form:  # Avoid empty forms
                    image = form['image']
                    PostImage.objects.create(post=post, image=image)
            
            messages.success(request, "Post created successfully!")
            return redirect('home')  # Adjust as needed
        else:
            messages.error(request, "Error in form submission.")
    else:
        post_form = PostForm()
        image_formset = ImageFormSet(queryset=PostImage.objects.none())

    return render(request, 'gobuybro/post_create.html', {
        'post_form': post_form,
        'image_formset': image_formset,
    })

@login_required
def my_posts(request):
    user_posts = Post.objects.filter(owner=request.user)
    return render(request, 'gobuybro/my_posts.html', {'posts': user_posts})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, owner=request.user)
    post.delete()
    return redirect('my_posts')

@login_required

def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # Create formset for PostImage
    ImageFormSet = modelformset_factory(PostImage, form=ImageForm, extra=1, can_delete=True)

    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES, instance=post)
        image_formset = ImageFormSet(request.POST, request.FILES, queryset=PostImage.objects.filter(post=post))

        if post_form.is_valid() and image_formset.is_valid():
            post_form.save()

            # Save images
            images = image_formset.save(commit=False)
            for image in images:
                image.post = post
                image.save()

            messages.success(request, "Post updated successfully!")
            return redirect('home')
        else:
            messages.error(request, "Error in form submission.")
    else:
        post_form = PostForm(instance=post)
        image_formset = ImageFormSet(queryset=PostImage.objects.filter(post=post))

    return render(request, 'gobuybro/edit_post.html', {
        'post_form': post_form,
        'image_formset': image_formset
    })
    
@login_required
def dashboard(request):
    profile = None  # Default value if user has no profile

    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()  # Get profile if exists

    return render(request, 'gobuybro/dashboard.html', {'profile': profile})

@login_required
def update_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('home')  # Redirect to home after updating the profile
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'gobuybro/update_profile.html', {'form': form})

def like_post(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)  # Remove dislike if it exists
        if request.user in post.likes.all():
            post.likes.remove(request.user)  # Unlike if already liked
            liked = False
        else:
            post.likes.add(request.user)  # Add like
            liked = True
        return JsonResponse({'liked': liked, 'likes_count': post.total_likes(), 'dislikes_count': post.total_dislikes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def dislike_post(request, post_id):
    if request.method == 'POST' and request.user.is_authenticated:
        post = get_object_or_404(Post, id=post_id)
        if request.user in post.likes.all():
            post.likes.remove(request.user)  # Remove like if it exists
        if request.user in post.dislikes.all():
            post.dislikes.remove(request.user)  # Remove dislike if already disliked
            disliked = False
        else:
            post.dislikes.add(request.user)  # Add dislike
            disliked = True
        return JsonResponse({'disliked': disliked, 'likes_count': post.total_likes(), 'dislikes_count': post.total_dislikes()})
    return JsonResponse({'error': 'Invalid request'}, status=400)