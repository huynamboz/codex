"""OPDS Utility classes."""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from django.utils.http import urlencode


BLANK_TITLE = "Unknown"


class OpdsNs:
    CATALOG = "http://opds-spec.org/2010/catalog"
    ACQUISITION = "http://opds-spec.org/2010/acquisition"


class UserAgents:
    """Control whether to hack in facets with nav links."""

    NO_FACET_SUPPORT = ("Panels", "Chunky")
    CLIENT_REORDERS = ("Chunky",)
    # FACET_SUPPORT = ("yar",) # kybooks


class TopRoutes:
    SERIES = {"group": "s", "pk": 0}
    FOLDER = {"group": "f", "pk": 0}
    ROOT = {"group": "r", "pk": 0}


class Rel:
    AUTHENTICATION = "http://opds-spec.org/auth/document"
    FACET = "http://opds-spec.org/facet"
    ACQUISITION = "http://opds-spec.org/acquisition"
    THUMBNAIL = "http://opds-spec.org/image/thumbnail"
    STREAM = "http://vaemendis.net/opds-pse/stream"
    SORT_NEW = "http://opds-spec.org/sort/new"
    SELF = "self"
    UP = "up"
    PREV = "prev"
    NEXT = "next"


class MimeType:
    ATOM = "application/atom+xml"
    _PROFILE_CATALOG = "profile=opds-catalog"
    NAV = ";".join((ATOM, _PROFILE_CATALOG, "kind=navigation"))
    ACQUISITION = ";".join((ATOM, _PROFILE_CATALOG, "kind=acquisition"))
    AUTHENTICATION = "application/opds-authentication+json"
    OPENSEARCH = "application/opensearchdescription+xml"
    DOWNLOAD = "application/vnd.comicbook+zip"
    STREAM = "image/jpeg"


@dataclass
class RootLink:
    rel: str
    mime_type: str = MimeType.NAV
    query_params: defaultdict[dict[str, Any]] = field(
        default_factory=lambda: defaultdict(dict)
    )


@dataclass
class FacetGroup:
    title_prefix: str
    query_param: str
    glyph: str
    facets: tuple


@dataclass
class Facet:
    value: str
    title: str


@dataclass
class TopLink:
    kwargs: dict
    root_link: RootLink
    glyph: str
    title: str


class RootLinks:
    UP = RootLink(Rel.UP)
    PREV = RootLink(Rel.PREV)
    NEXT = RootLink(Rel.NEXT)
    NEW = RootLink(
        Rel.SORT_NEW,
        MimeType.ACQUISITION,
        {"orderBy": "date", "orderReverse": True},
    )


class TopLinks:
    NEW = TopLink(
        TopRoutes.SERIES,
        RootLinks.NEW,
        "📥",
        "New",
    )


class FacetGroups:
    ORDER_BY = FacetGroup(
        "Order By",
        "orderBy",
        "➠",
        (
            Facet("date", "Date"),
            Facet("sort_name", "Name"),
            Facet("search_score", "Search Score"),
        ),
    )
    TOP_GROUP = FacetGroup(
        "",
        "topGroup",
        "⊙",
        (Facet("p", "Publishers View"), Facet("s", "Series View")),
    )
    ORDER_REVERSE = FacetGroup(
        "Order",
        "orderReverse",
        "⇕",
        (Facet("false", "Ascending"), Facet("true", "Descending")),
    )


DEFAULT_FACETS = {
    "topGroup": "p",
    "orderBy": "sort_name",
    "orderReverse": "false",
}


@dataclass
class OPDSLink:
    rel: str
    href: str
    type: str
    title: str = ""
    length: int = 0
    facet_group: str = ""
    facet_active: bool = False
    thr_count: int = 0
    pse_count: int = 0
    pse_last_read: int = 0


def update_href_query_params(href, old_query_params, new_query_params):
    query_params = {}
    for key, value in old_query_params.items():
        # qps are sometimes encapsulated in a list for when there's mutiples.
        if isinstance(value, list):
            if len(value):
                query_params[key] = value[0]
        else:
            query_params[key] = value
    query_params.update(new_query_params)
    if query_params:
        href += "?" + urlencode(query_params, doseq=True)
    return href