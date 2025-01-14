"""Reader session view."""

from codex.serializers.reader import ReaderSettingsSerializer
from codex.views.settings import SettingsView


class ReaderSettingsView(SettingsView):
    """Get Reader Settings."""

    serializer_class = ReaderSettingsSerializer

    SESSION_KEY = "reader"
