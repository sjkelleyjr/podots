import uuid
import requests

from django.contrib.auth.models import AbstractUser
from django.urls import reverse

from django.db import models

from django.utils import timezone
import datetime

import  hashlib
from urllib.parse import urlencode

from mptt.models import MPTTModel, TreeForeignKey


#class CustomUser(MPTTModel, AbstractUser):
class CustomUser(AbstractUser, MPTTModel):
    class Meta:
        default_manager_name = 'objects'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    karma = models.IntegerField(default=0)
    about = models.TextField(default='')
    # api_key = models.CharField(max_length=100)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='invitees', editable=False)

    used_invitation = models.ForeignKey('Invitation', null=True, default=None, on_delete=models.CASCADE)

    def get_absolute_url(self):
        return reverse("accounts_profile", kwargs={"username": self.username})

    @property
    def is_green(self):
        return timezone.now() - self.date_joined < datetime.timedelta(days=30)

    def gravatar_url(self, size=80):
        if self.email:
            default = "/static/user.png"
            url = "https://www.gravatar.com/avatar/" + hashlib.md5(self.email.lower().encode('utf-8')).hexdigest() + "?"
            url += urlencode({'d':default, 's':str(size)})

            #check if the image is valid
            image_formats = ("image/png", "image/jpeg", "image/jpg")
            r = requests.head(url)

            if r.headers["content-type"] in image_formats:
                return url
            else:
                return default
        else:
            default = "/static/user.png"
            return default

    @property
    def latest_verified_email(self):
        verifications = EmailVerification.objects.filter(user=self, verified=True).order_by('-verified_at')
        if verifications.count():
            return verifications[0].email



class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    inviting_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    num_signups = models.PositiveIntegerField(null=True, default=1)
    invited_email_address = models.EmailField(null=True, default=None)

    invite_code = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)

    def get_absolute_url(self):
        return reverse("accounts_invite", kwargs={"pk": self.pk})

    def get_register_url(self):
        return reverse("accounts_register") + '?invite=' + str(self.invite_code)

    @property
    def active(self):
        return True
        pass # TODO


class EmailVerification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)
    verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True)

    email = models.EmailField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    verification_code = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)

    def get_verify_url(self):
        return reverse("accounts_verify", kwargs={"verification_code": self.verification_code})


class PasswordResetRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    email = models.EmailField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    verification_code = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)


    def get_verify_url(self):
        return reverse("password_forgotten", kwargs={"verification_code": self.verification_code})
