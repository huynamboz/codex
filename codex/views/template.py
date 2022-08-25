"""Generic Codex Template View."""
from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView


class TemplateXMLRenderer(TemplateHTMLRenderer):

    media_type = "text/xml"
    format = "xml"


class SimpleAPIView(APIView):

    content_type = "text/html"
    status_code = status.HTTP_200_OK

    def get(self, request, *args, **kwargs):
        """Render the template with correct content_type."""
        return Response(
            data={}, status=self.status_code, content_type=self.content_type
        )


class CodexTemplateView(SimpleAPIView):
    """Template View."""

    renderer_classes = [TemplateHTMLRenderer]
    content_type = "text/html"


class CodexXMLTemplateView(SimpleAPIView):

    renderer_classes = [TemplateXMLRenderer]
    content_type = "application/xml"