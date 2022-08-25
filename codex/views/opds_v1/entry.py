"""OPDS Entry."""
import math

from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse

from codex.settings.logging import get_logger
from codex.views.opds_v1.util import (
    BLANK_TITLE,
    MimeType,
    OPDSLink,
    Rel,
    update_href_query_params,
)


LOG = get_logger(__name__)


class OPDSEntry:

    _DATE_FORMAT_BASE = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT_MS = _DATE_FORMAT_BASE + ".%f%z"
    DATE_FORMAT = _DATE_FORMAT_BASE + "%z"
    DATE_FORMATS = (DATE_FORMAT_MS, DATE_FORMAT)

    def __init__(self, obj, valid_nav_groups, query_params, at_top=False):
        self.obj = obj
        self.valid_nav_groups = valid_nav_groups
        self.query_params = query_params
        self.at_top = at_top

    @staticmethod
    def _compute_zero_pad(issue_max):
        """Compute zero padding for issues."""
        if not issue_max or issue_max < 1:
            return 1
        return math.floor(math.log10(issue_max)) + 1

    @property
    def id(self):
        """GUID is a nav url."""
        group = self.obj.get("group")
        pk = self.obj.get("pk")
        return reverse("opds:v1:browser", kwargs={"group": group, "pk": pk, "page": 1})

    @property
    def title(self):
        """Compute the item title."""
        group = self.obj.get("group")
        parts = []
        if group == "i":
            parts.append(self.obj.get("publisher_name"))
        elif group == "v":
            parts.append(self.obj.get("series_name"))
        elif group == "c":
            if self.at_top:
                parts.append(self.obj.get("series_name"))

            issue_max = self.obj.get("issue_max")
            zero_pad = self._compute_zero_pad(issue_max)
            issue = self.obj.get("issue")
            if issue is None:
                issue = Decimal(0)
            issue = issue.normalize()
            issue_suffix = self.obj.get("issue_suffix", "")

            int_issue = math.floor(issue)
            if issue == int_issue:
                issue_str = str(int_issue)
            else:
                issue_str = str(issue)
                decimal_parts = issue_str.split(".")
                if len(decimal_parts) > 1:
                    zero_pad += len(decimal_parts[1]) + 1

            issue_num = issue_str.zfill(zero_pad)
            full_issue_str = f"#{issue_num}{issue_suffix}"
            parts.append(full_issue_str)

        if name := self.obj.get("name"):
            parts.append(name)

        result = " ".join(parts)
        if not result:
            result = BLANK_TITLE
        return result

    @property
    def issued(self):
        if date := self.obj.get("date"):
            return date

    @property
    def updated(self):
        if updated_at := self.obj.get("updated_at"):
            updated = None
            try:
                for format in self.DATE_FORMATS:
                    try:
                        updated = datetime.strptime(updated_at, format)
                        updated = updated.astimezone(timezone.utc)
                        break
                    except ValueError:
                        pass
            except Exception as exc:
                LOG.warning(exc)
            return updated

    @property
    def summary(self):
        """Return a child count or comic summary."""
        if self.obj.get("group") == "c":
            desc = self.obj.get("summary")
        elif children := self.obj.get("child_count"):
            desc = f"{children} issues"
        else:
            desc = None

        return desc

    def _thumb_link(self):
        cover_pk = self.obj.get("cover_pk")
        if cover_pk:
            kwargs = {"pk": cover_pk}
            href = reverse("opds:v1:cover", kwargs=kwargs)
        elif cover_pk == 0:
            href = staticfiles_storage.url("img/missing_cover.webp")
        else:
            return
        return OPDSLink(Rel.THUMBNAIL, href, "image/webp")

    def _nav_link(self):
        group = self.obj.get("group")
        pk = self.obj.get("pk")
        kwargs = {"group": group, "pk": pk, "page": 1}

        try:
            group_index = self.valid_nav_groups.index(group)
            aq_link = group_index + 1 >= len(self.valid_nav_groups)
        except Exception:
            aq_link = False

        if aq_link:
            mime_type = MimeType.ACQUISITION
        else:
            mime_type = MimeType.NAV

        href = reverse("opds:v1:browser", kwargs=kwargs)
        href = update_href_query_params(
            href, self.query_params, self.obj.get("query_params", {})
        )
        thr_count = self.obj.get("child_count")

        return OPDSLink("subsection", href, mime_type, thr_count=thr_count)

    def _download_link(self):
        pk = self.obj.get("pk")
        if not pk:
            return
        kwargs = {"pk": pk}
        return OPDSLink(
            Rel.ACQUISITION,
            reverse("opds:v1:download", kwargs=kwargs),
            MimeType.DOWNLOAD,
            length=self.obj.get("size", 1),
        )

    def _stream_link(self):
        pk = self.obj.get("pk")
        if not pk:
            return
        base_url = reverse("opds:v1:start")
        href = f"{base_url}c/{pk}/" + "{pageNumber}/page.jpg?bookmark=1"
        count = self.obj.get("page_count")
        page = self.obj.get("page", 0)
        return OPDSLink(
            Rel.STREAM,
            href,
            MimeType.STREAM,
            pse_count=count,
            pse_last_read=page,
        )

    @property
    def links(self):
        result = []
        if thumb := self._thumb_link():
            result += [thumb]

        if self.obj.get("group") == "c":
            if download := self._download_link():
                result += [download]
            if stream := self._stream_link():
                result += [stream]
        else:
            if nav := self._nav_link():
                result += [nav]

        return result