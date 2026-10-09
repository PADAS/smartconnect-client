"""Rules shared by er-smart-sync and cdip-routing for ER Choice values.

EarthRanger v2 event types store LIST/MLIST/TREE selections as ``Choice``
records whose ``value`` must match ``^\\w+$`` and is capped at 100
characters. er-smart-sync derives those values from SMART option keys when
it pushes a data model; cdip-routing applies the inverse when an ER event
comes back so SMART Connect receives the option key it knows.

These rules are load-bearing. Sites that already synced carry Choice rows
and historical events derived with them, so changing any function here
means rewriting stored data on every such site.
"""
import hashlib
import re
from typing import Iterable, List

CHOICE_VALUE_MAX_LEN = 100
_VALUE_HASH_LEN = 8
# Readable prefix kept before "_{hash}": 100 - 1 - 8.
_VALUE_PREFIX_LEN = CHOICE_VALUE_MAX_LEN - 1 - _VALUE_HASH_LEN


class OptionKeyResolutionError(ValueError):
    """A Choice value could not be mapped back to exactly one option key."""


class UnresolvableOptionKey(OptionKeyResolutionError):
    """No option key produces the given Choice value."""


class AmbiguousOptionKey(OptionKeyResolutionError):
    """More than one option key produces the given Choice value."""


def sanitize_choice_value(option_key: str) -> str:
    """Map a SMART option key to a ``^\\w+$`` string.

    SMART keys may contain ``.`` (TREE leaf paths), accents, apostrophes and
    spaces. Runs of anything outside ASCII letters and digits collapse to a
    single underscore, leading and trailing underscores are dropped, and the
    result is lower-cased. An empty result becomes ``"_"``.
    """
    sanitized = re.sub(r"[^A-Za-z0-9]+", "_", option_key).strip("_").lower()
    return sanitized or "_"


def shorten_choice_value(sanitized: str) -> str:
    """Hash-suffix values longer than ``CHOICE_VALUE_MAX_LEN``.

    Deterministic: the same input always yields the same output, and two
    inputs sharing the first 91 characters get different hash tails.
    """
    if len(sanitized) <= CHOICE_VALUE_MAX_LEN:
        return sanitized
    digest = hashlib.sha256(sanitized.encode("utf-8")).hexdigest()[:_VALUE_HASH_LEN]
    return f"{sanitized[:_VALUE_PREFIX_LEN]}_{digest}"


def choice_value_for_option_key(option_key: str) -> str:
    """The ER Choice value er-smart-sync stores for ``option_key``."""
    return shorten_choice_value(sanitize_choice_value(option_key))


def resolve_option_key(option_keys: Iterable[str], value: str) -> str:
    """Return the SMART option key that an ER Choice value came from.

    An exact match on a key wins. Otherwise the single key whose Choice
    value equals ``value`` is returned. Raises ``UnresolvableOptionKey``
    when nothing matches or ``value`` is not a string, and
    ``AmbiguousOptionKey`` when several keys collapse to the same value.
    """
    if not isinstance(value, str):
        raise UnresolvableOptionKey(
            f"Choice value must be a string, got {type(value).__name__}: {value!r}"
        )
    keys: List[str] = list(option_keys)
    if value in keys:
        return value
    matches = [key for key in keys if choice_value_for_option_key(key) == value]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise UnresolvableOptionKey(f"No option key maps to choice value {value!r}")
    raise AmbiguousOptionKey(
        f"Choice value {value!r} maps to several option keys: {matches}"
    )
