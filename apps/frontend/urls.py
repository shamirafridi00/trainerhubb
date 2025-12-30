# HTMX Legacy URLs - DEPRECATED
# Re-export from legacy location for compatibility
from apps.frontend_legacy import urls as frontend_legacy_urls
urlpatterns = frontend_legacy_urls.urlpatterns
app_name = frontend_legacy_urls.app_name