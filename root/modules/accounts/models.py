from email.policy import default
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from cloudinary.models import CloudinaryField
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class UserAccountManager(BaseUserManager):
    def create_user(self, username, email, name, role='Guest', is_staff=False, is_superuser=False, password=None):
        print(email)
        if not name:
            raise ValueError('User must have name')

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            name=name,
            role=role,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, name, role='Admin', is_staff=True, is_superuser=True, password=None):
        user = self.create_user(
            username=username,
            email=email,
            name=name,
            role=role,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        return user


class UserAccount(AbstractBaseUser, PermissionsMixin):
    class Meta:
        app_label = 'accounts'

    class Role(models.TextChoices):
        ADMIN = 'Admin'
        MENTOR = 'Mentor'
        GUEST = 'Guest'

    email = models.EmailField(max_length=255, unique=True, db_index=True)
    username = models.CharField(
        max_length=255, unique=True, db_index=True, null=True, blank=True)
    name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=15, choices=Role.choices, default='Guest', db_index=True)
    is_staff = models.BooleanField(default=False)
    profile_photo = CloudinaryField('image', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    phone_number = PhoneNumberField(blank=True, db_index=True)

    objects = UserAccountManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name', 'role', 'email']

    def __str__(self):
        return self.name
