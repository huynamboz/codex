"""Query the missing foreign keys for comics and credits."""
from logging import getLogger
from pathlib import Path

from django.db.models import Q

from codex.models import Comic, Credit, Folder, Imprint, Publisher, Series, Volume


CREDIT_FKS = ("role", "person")

CREDIT_QUERY_FIELDS = ("role__name", "person__name")
FOLDER_QUERY_FIELDS = ("path",)
QUERY_FIELDS = {
    Credit: ("role__name", "person__name"),
    Folder: ("path",),
    Imprint: ("publisher__name", "name"),
    Series: ("publisher__name", "imprint__name", "name"),
    Volume: ("publisher__name", "imprint__name", "series__name", "name"),
}
NAMED_MODEL_QUERY_FIELDS = ("name",)
# sqlite parser breaks with more than 1000 lines in a query and django only fixes this
# in the bulk_create & bulk_update functions. So for complicated queries I gotta batch
# them myself
# Filter arg count is a poor proxy for sql line length and variables but it works
#   1998 is too high for the Credit query, for instance.
FILTER_ARG_MAX = 1950
LOG = getLogger(__name__)


def _query_existing_mds(fk_cls, filter):
    """Query existing metatata tables."""
    fields = QUERY_FIELDS.get(fk_cls, NAMED_MODEL_QUERY_FIELDS)
    flat = len(fields) == 1 and fk_cls != Publisher

    existing_mds = set(
        fk_cls.objects.filter(filter).order_by("pk").values_list(*fields, flat=flat)
    )
    return existing_mds


def _query_create_metadata(fk_cls, create_mds, all_filter_args):
    """Get create metadata by comparing proposed meatada to existing rows."""
    # Do this in batches so as not to exceed the 1k line sqlite limit
    filter = Q()
    filter_arg_count = 0
    all_filter_args = tuple(all_filter_args)
    num = 0

    for filter_args in all_filter_args:
        filter = filter | Q(**dict(filter_args))
        filter_arg_count += len(filter_args)
        if filter_arg_count >= FILTER_ARG_MAX or filter_args == all_filter_args[-1]:
            # If too many filter args in the query or we're on the last one.
            create_mds -= _query_existing_mds(fk_cls, filter)

            # Log
            num += 1
            LOG.debug(f"Queried for existing {fk_cls.__name__}s, batch {num}")

            # Reset the filter
            filter = Q()
            filter_arg_count = 0

    return create_mds


def _add_parent_group_filter(group_name, field_name, filter_args):
    """Get the parent group filter by name."""
    if field_name:
        key = f"{field_name}__"
    else:
        key = ""

    key += "name"

    filter_args[key] = group_name


def _query_missing_group_type(fk_cls, groups):
    """Get missing groups from proposed groups to create."""
    # create the filters
    candidates = {}
    all_filter_args = set()
    for group_tree, count in groups.items():
        filter_args = {}
        _add_parent_group_filter(group_tree[-1], "", filter_args)
        if fk_cls in (Imprint, Series, Volume):
            _add_parent_group_filter(group_tree[0], "publisher", filter_args)
        if fk_cls in (Series, Volume):
            _add_parent_group_filter(group_tree[1], "imprint", filter_args)
        if fk_cls == Volume:
            _add_parent_group_filter(group_tree[2], "series", filter_args)

        all_filter_args.add(tuple(sorted(filter_args.items())))
        candidates[group_tree] = count

    # get the create metadata
    candidate_groups = set(candidates.keys())
    create_group_set = _query_create_metadata(fk_cls, candidate_groups, all_filter_args)

    # Append the count metadata to the create_groups
    create_groups = {}
    for group, count_dict in candidates.items():
        if group in create_group_set:
            create_groups[group] = count_dict
    return create_groups


def _query_missing_groups(group_trees_md):
    """Get missing groups from proposed groups to create."""
    # XXX Missing a facility to update Series & Volume count fields on already
    #     created groups

    all_create_groups = {}
    count = 0
    for cls, groups in group_trees_md.items():
        create_groups = _query_missing_group_type(cls, groups)
        all_create_groups[cls] = create_groups
        if create_groups:
            count += 1
    return all_create_groups, count


def _query_missing_credits(credits):
    """Find missing credit objects."""
    # create the filter
    comparison_credits = set()
    all_filter_args = set()
    for credit_tuple in credits:
        credit_dict = dict(credit_tuple)
        role = credit_dict.get("role")
        person = credit_dict["person"]
        filter_args = {
            "person__name": person,
            "role__name": role,
        }
        all_filter_args.add(tuple(sorted(filter_args.items())))

        comparison_tuple = (role, person)
        comparison_credits.add(comparison_tuple)

    # get the create metadata
    create_credits = _query_create_metadata(Credit, comparison_credits, all_filter_args)

    return create_credits


def _query_missing_simple_models(base_cls, field, fk_field, names):
    """Find missing named models and folders."""
    # Do this in batches so as not to exceed the 1k line sqlite limit
    fk_cls = base_cls._meta.get_field(field).related_model

    offset = 0
    proposed_names = list(names)
    create_names = set(names)
    num_proposed_names = len(proposed_names)
    num = 0
    while offset < num_proposed_names:
        end = offset + FILTER_ARG_MAX
        filter_args = {f"{fk_field}__in": proposed_names[offset:end]}
        filter = Q(**filter_args)
        create_names -= _query_existing_mds(fk_cls, filter)
        num += 1
        LOG.debug(f"Queried for existing {fk_cls.__name__}s, batch {num}")
        offset += FILTER_ARG_MAX

    return fk_cls, create_names


def query_missing_folder_paths(library_path, comic_paths):
    """Find missing folder paths."""
    # Get the proposed folder_paths
    library_path = Path(library_path)
    proposed_folder_paths = set()
    for comic_path in comic_paths:
        for path in Path(comic_path).parents:
            if path.is_relative_to(library_path) and path != library_path:
                proposed_folder_paths.add(str(path))

    # get the create metadata
    _, create_folder_paths = _query_missing_simple_models(
        Comic, "parent_folder", "path", proposed_folder_paths
    )

    return create_folder_paths


def query_all_missing_fks(library_path, fks):
    """Get objects to create by querying existing objects for the proposed fks."""
    LOG.verbose(  # type: ignore
        f"Querying existing foreign keys for comics in {library_path}"
    )
    create_credits = set()
    if "credits" in fks:
        credits = fks.pop("credits")
        create_credits |= _query_missing_credits(credits)
    LOG.verbose(f"Prepared {len(create_credits)} new credits.")  # type: ignore

    create_groups = {}
    if "group_trees" in fks:
        group_trees = fks.pop("group_trees")
        create_groups, create_group_count = _query_missing_groups(group_trees)
    LOG.verbose(f"Prepared {create_group_count} new groups.")  # type: ignore

    create_paths = set()
    if "comic_paths" in fks:
        create_paths |= query_missing_folder_paths(library_path, fks.pop("comic_paths"))
    LOG.verbose(f"Prepared {len(create_paths)} new folders.")  # type: ignore

    create_fks = {}
    total_create_fks = 0
    for field in fks.keys():
        names = fks.get(field)
        if field in CREDIT_FKS:
            base_cls = Credit
        else:
            base_cls = Comic
        cls, names = _query_missing_simple_models(base_cls, field, "name", names)
        create_fks[cls] = names
        total_create_fks += len(names)
    LOG.verbose(f"Prepared {total_create_fks} new named attributes.")  # type: ignore

    return create_fks, create_groups, create_paths, create_credits