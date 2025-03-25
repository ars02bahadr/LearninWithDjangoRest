from django.db import models
from django.contrib.auth.models import User

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserType(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        app_label = 'api'
        verbose_name = 'Kullanıcı Tipi'
        verbose_name_plural = 'Kullanıcı Tipleri'

    def __str__(self):
        return self.name


class UserRole(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        app_label = 'api'
        verbose_name = 'Kullanıcı Rolü'
        verbose_name_plural = 'Kullanıcı Rolleri'

    def __str__(self):
        return self.name
    

class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True)
    user_roles = models.ManyToManyField(UserRole)

    class Meta:
        app_label = 'api'
        verbose_name = 'Kullanıcı Profili'
        verbose_name_plural = 'Kullanıcı Profilleri'

    def __str__(self):
        return f"{self.user.get_full_name()}"
    
    
