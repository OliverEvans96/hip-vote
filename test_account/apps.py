from importlib import import_module

from django.apps import AppConfig as BaseAppConfig


class AppConfig(BaseAppConfig):

    name = "test_account"

    def ready(self):
        import_module("test_account.receivers")
