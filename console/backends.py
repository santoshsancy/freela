import logging
from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend, RemoteUserBackend

logger = logging.getLogger(__name__)

class EmailOrUsernameBackend(ModelBackend):
    AUTH_OPTIONS = ['email']

    def authenticate(self, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except:
                user = UserModel._default_manager.get(email=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

class UMRemoteUserBackend(RemoteUserBackend):

    def configure_user(self, user):
        setattr(user, 'email', '%s@umich.edu' % user.username)
        user.set_password(get_user_model().objects.make_random_password())
        if not user.setup_completed:
            user.setup_completed = datetime.now()
        user = user.save()
        return user
