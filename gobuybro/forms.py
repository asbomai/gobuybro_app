from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, PostImage, Profile
from django.forms import modelformset_factory

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['email','username','password1','password2']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'location', 'description', 'video', 'purchase_currency', 'rent_currency']

    def clean(self):
        cleaned_data = super().clean()
        
        # Set purchase_currency and rent_currency to None if empty
        if not cleaned_data.get('purchase_currency'):
            cleaned_data['purchase_currency'] = None
        if not cleaned_data.get('rent_currency'):
            cleaned_data['rent_currency'] = None
            
        return cleaned_data
        
class ImageForm(forms.ModelForm):
    class Meta:
        model = PostImage
        fields = ['image']

# Define the formset for handling multiple images
ImageFormSet = forms.modelformset_factory(
    PostImage,
    form=ImageForm,
    extra=3,  # Allow up to 3 images to be uploaded
    can_delete=True  # Optional: Allow users to delete uploaded images
)

class ProfileForm(forms.ModelForm):
    class Meta:

        model = Profile
        fields = ['profile_photo','business_name','business_address','phone_number']