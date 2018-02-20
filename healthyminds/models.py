# This Python file uses the following encoding: utf-8

import logging
import json
import bleach
import re

from itertools import chain
from random import randint, choice, shuffle, seed, Random
from datetime import date, datetime, timedelta, time
from operator import itemgetter
from django.conf import settings

from django.db import models
from django.db.models import F, Q, Count, Avg, Sum, Min, Max, Func, Case, When
from django.db.models.signals import post_save
from django_extensions.db.models import  TitleSlugDescriptionModel, TimeStampedModel

from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        UserManager, PermissionsMixin)
from django.contrib.staticfiles.templatetags.staticfiles import static

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.utils import timezone

from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

class AccountManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')
        email = UserManager.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=False, is_active=True, is_superuser=False,
                          last_login=now, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        u = self.create_user(username, email, password, **extra_fields)
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True
        u.save(using=self._db)
        return u

class Account(AbstractBaseUser, PermissionsMixin):
    objects = AccountManager()

    username = models.CharField('username', max_length=50, unique=True, db_index=True)
    email = models.EmailField('email address', max_length=254, unique=True)
    account_id = models.IntegerField(blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)

    setup_completed = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    is_staff = models.BooleanField('Admin Access', default=False,
                                   help_text='Designates whether this user can perform platform administrative actions.')

    is_active = models.BooleanField('active', default=True,
                                    help_text='Designates whether this user should be treated as '
                                    'active. Unselect this instead of deleting accounts.')

    @property
    def staff_access(self):
        return self.is_staff or self.is_superuser

    @property
    def short_name(self):
        return self.first_name

    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)

class Institution(TimeStampedModel):
    name = models.CharField(max_length=50)
    default_source = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    @classmethod
    def default_institution(cls):
        return cls.objects.get_or_create(name="University of Michigan", default_source="UM")[0]
