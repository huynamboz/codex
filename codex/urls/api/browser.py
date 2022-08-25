"""codex:api:v3:browser URL Configuration."""
from django.urls import path
from django.views.decorators.cache import cache_page, never_cache

from codex.views.bookmark import BookmarkView
from codex.views.browser.browser import BrowserView
from codex.views.browser.choices import BrowserChoiceView
from codex.views.browser.metadata import MetadataView
from codex.views.browser.session import BrowserSessionView


TIMEOUT = 60 * 5


app_name = "browser"
urlpatterns = [
    #
    #
    # Browser
    path(
        "<int:pk>/<int:page>",
        cache_page(TIMEOUT)(BrowserView.as_view()),
        name="page",
    ),
    path(
        "<int:pk>/choices/<str:field_name>",
        cache_page(TIMEOUT)(BrowserChoiceView.as_view()),
        name="choices",
    ),
    path(
        "<int:pk>/metadata",
        cache_page(TIMEOUT)(MetadataView.as_view()),
        name="metadata",
    ),
    #
    #
    # Bookmark
    path(
        "<int:pk>/settings",
        BookmarkView.as_view(),
        name="group_settings",
    ),
    path("settings", never_cache(BrowserSessionView.as_view()), name="settings"),
]