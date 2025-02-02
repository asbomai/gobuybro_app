from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver 
from django.conf import settings
from djmoney.models.fields import MoneyField
from django.core.validators import RegexValidator


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    description = models.TextField()
    video = models.FileField(upload_to='videos/')
    purchase_currency = MoneyField(max_digits=11, decimal_places=2, default_currency='NGN', blank=True, null=True)
    rent_currency = MoneyField(max_digits=11, decimal_places=2, default_currency='NGN', blank=True, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    dislikes = models.ManyToManyField(User, related_name='disliked_posts', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_likes(self):
        return self.likes.count()

    def total_dislikes(self):
        return self.dislikes.count()
  
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.text[:20]}"
        
class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_photo = models.ImageField(upload_to='profile_photos/', default='profile_photos/p-image.png')
    business_name = models.CharField(max_length=250)
    business_address = models.CharField(max_length=250)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',  # Example: +1234567890 or 1234567890
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
    validators=[phone_regex],
    max_length=17,
    blank=True,
    null=True,
    default=''  # Provide a default value (e.g., empty string)
)
    
    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()