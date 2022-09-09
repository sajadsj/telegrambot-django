import debug_toolbar
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("tgadmin/", admin.site.urls),
    path("", include("tgbot.urls")),
    path("__debug__/", include(debug_toolbar.urls)),
]
