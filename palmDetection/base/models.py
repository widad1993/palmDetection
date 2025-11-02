from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# مدير المستخدم
class UserAccountManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError("Users must have a username")

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None):
        user = self.create_user(username, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# نموذج المستخدم
class UserAccount(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.name if self.name else self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

class Technician(models.Model):
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255) 
    last_login = models.DateTimeField(auto_now=True)
    plain_password = models.CharField(max_length=255, null=True, blank=True)

# نموذج المزرعة
class Farm(models.Model):
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    subscription = models.CharField(max_length=255, blank=True, null=True)

class FarmHistory(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    image = models.CharField(max_length=255)
    damage_type = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)    

    def __str__(self):
        return self.name
