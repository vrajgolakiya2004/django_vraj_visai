from django.db import models
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password

class User(models.Model):
    name = models.CharField(max_length=800, null=True, blank=True, default=None)
    email = models.EmailField(max_length=800, null=True, blank=True, default=None)
    phone = models.CharField(max_length=800, null=True, blank=True, default=None)
    password = models.CharField(max_length=800, null=True, blank=True, default=None)
    check_password = models.CharField(max_length=800, null=True, blank=True, default=None)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True, default=None)
    created_at = models.DateTimeField(default=now,db_column='created_at')

   

    class Meta:
        db_table = 'registertbl'

# print("tirth-------------models.py------------------------------------",User,'v',User.email)
def save(self, *args, **kwargs):
        # Hash the password with Argon2 if it’s not already hashed
        if self.password and not self.password.startswith('argon2$'):
            self.password = make_password(self.password)
        # Optionally hash check_password (not recommended, see note below)
        if self.check_password and not self.check_password.startswith('argon2$'):
            self.check_password = make_password(self.check_password)
        super().save(*args, **kwargs)
def __str__(self):
        
        return self.email