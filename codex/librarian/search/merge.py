"""Search Index Merging for Read Optimization."""
from time import time
from typing import TYPE_CHECKING

from humanize import naturaldelta

from codex.librarian.mp_queue import LIBRARIAN_QUEUE
from codex.librarian.search.status import SearchIndexStatusTypes
from codex.librarian.search.tasks import SearchIndexRemoveStaleTask
from codex.librarian.search.version import VersionMixin
from codex.settings.settings import SEARCH_INDEX_PATH
from codex.status import Status

if TYPE_CHECKING:
    from codex.search.backend import CodexSearchBackend


class MergeMixin(VersionMixin):
    """Search Index Merge Methods."""

    def _is_index_optimized(self, num_segments):
        """Is the index already in one segment."""
        if num_segments <= 1:
            self.log.info("Search index already optimized.")
            return True
        return False

    def merge_search_index(self, optimize=False):
        """Optimize search index."""
        name = "all segments" if optimize else "small segments"
        status = Status(SearchIndexStatusTypes.SEARCH_INDEX_MERGE.value, subtitle=name)
        try:
            statii = (
                status,
                Status(SearchIndexStatusTypes.SEARCH_INDEX_REMOVE.value),
            )
            self.status_controller.start_many(statii)
            start = time()

            old_num_segments = len(tuple(SEARCH_INDEX_PATH.glob("*.seg")))
            if self._is_index_optimized(old_num_segments):
                return

            # Optimize
            method = "into one" if optimize else "small segments"
            self.log.info(
                f"Search index found in {old_num_segments} segments,"
                f" merging {method}..."
            )
            backend: CodexSearchBackend = self.engine.get_backend()  # type: ignore
            if optimize:
                backend.optimize()
            else:
                backend.merge_small()

            # Finish
            new_num_segments = len(tuple(SEARCH_INDEX_PATH.glob("*.seg")))
            diff = old_num_segments - new_num_segments
            elapsed_time = time() - start
            elapsed = naturaldelta(elapsed_time)
            if diff:
                self.log.info(f"Merged {diff} search index segments in {elapsed}.")
            else:
                self.log.info("No small search index segments found.")
            LIBRARIAN_QUEUE.put(SearchIndexRemoveStaleTask())
        except Exception:
            self.log.exception("Search index merge.")
            self.status_controller.finish(
                SearchIndexStatusTypes.SEARCH_INDEX_REMOVE.value, notify=False
            )
        finally:
            self.status_controller.finish(status)
