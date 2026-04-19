"""Vendored copy of the GapTree layout sorting algorithm.

The upstream project (https://github.com/hiroi-sora/GapTree_Sort_Algorithm) is
declared as a git submodule at ``src/ocr_loader/GapTree_Sort_Algorithm``, but
the pinned revision is no longer fetchable from its remote. The single module
needed here is therefore vendored locally so multi-column reading order keeps
working without network access. See ``LICENSE`` in this folder.
"""

from .gap_tree import GapTree

__all__ = ["GapTree"]