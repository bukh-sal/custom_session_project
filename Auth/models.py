from django.contrib.sessions.backends.db import SessionStore as DBStore
from django.contrib.sessions.base_session import AbstractBaseSession
from django.db import models

class Session(AbstractBaseSession):
    custom_field = models.CharField(max_length=255)
    hashed_session_key = models.CharField(max_length=255, unique=True)

    @classmethod
    def get_session_store_class(cls):
        return SessionStore
    
    def hash_key(self):
        import hashlib
        SALT = "BLOCKCHAIN_IS_A_GOOD_TECHNOLOGY"
        joined = SALT + self.session_key
        return hashlib.sha256(joined.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.hashed_session_key:
            self.hashed_session_key = self.hash_key()
            self.save()
        print("Session saved!")

class SessionStore(DBStore):
    @classmethod
    def get_model_class(cls):
        return Session

    def create_model_instance(self, data):
        obj = super().create_model_instance(data)
        try:
            account_id = int(data.get("_auth_user_id"))
        except (ValueError, TypeError):
            account_id = None
        obj.account_id = account_id
        return obj


class Request(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=255)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.path}"