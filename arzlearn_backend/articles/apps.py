from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'
    verbose_name = 'مقالات و دسته‌بندی‌ها'

    def ready(self):
        import articles.signals  # noqa: F401
