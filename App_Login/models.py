from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

# Profile model (extends built-in User)
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    # Role flag
    is_supplier = models.BooleanField(default=False)

    # Optional customer info
    address = models.CharField(max_length=300, blank=True)
    city = models.CharField(max_length=40, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.user.username} profile"

@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    """A signal to create a profile when a user is created"""
    if created:
        #if created then automatically create a profile object
        Profile.objects.create(user=instance)

@receiver(post_save,sender=User)
def save_profile(sender,instance,**kwargs):
    """A signal to save a profile when a user is saved"""
    instance.profile.save()