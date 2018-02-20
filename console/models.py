import logging, sys
import random
import os

from random import randint
from datetime import datetime, timedelta

from django.db import models
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist

from django_extensions.db.models import  TitleSlugDescriptionModel, TimeStampedModel
from django.utils.translation import ugettext_lazy as _

from django.db import models, transaction
from django.conf import settings

logger = logging.getLogger(__name__)
