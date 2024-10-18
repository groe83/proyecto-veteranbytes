from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(
        self,
        email,
        rut,
        nombres,
        apellido_paterno,
        apellido_materno,
        password=None,
        **extra_fields,
    ):
        if not email:
            raise ValueError(_("El correo electrónico es obligatorio"))
        if not rut:
            raise ValueError(_("El RUT es obligatorio"))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            rut=rut,
            nombres=nombres,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email,
        rut,
        nombres,
        apellido_paterno,
        apellido_materno,
        password=None,
        **extra_fields,
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(
            email,
            rut,
            nombres,
            apellido_paterno,
            apellido_materno,
            password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    rut = models.CharField(_("RUT"), max_length=12, unique=True)
    nombres = models.CharField(_("Nombres"), max_length=150)
    apellido_paterno = models.CharField(_("Apellido Paterno"), max_length=150)
    apellido_materno = models.CharField(_("Apellido Materno"), max_length=150)
    email = models.EmailField(_("Email"), unique=True)
    fecha_registro = models.DateTimeField(_("Fecha de Registro"), auto_now_add=True)
    is_active = models.BooleanField(_("Activo"), default=True)
    is_staff = models.BooleanField(_("Staff"), default=False)
    is_superuser = models.BooleanField(_("Superuser"), default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["rut", "nombres", "apellido_paterno", "apellido_materno"]

    objects = UserManager()

    def __str__(self):
        return f"{self.email} - {self.rut}"
