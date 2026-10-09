import hashlib

import pytest

from smartconnect.choices import (
    CHOICE_VALUE_MAX_LEN,
    AmbiguousOptionKey,
    OptionKeyResolutionError,
    UnresolvableOptionKey,
    choice_value_for_option_key,
    resolve_option_key,
    sanitize_choice_value,
    shorten_choice_value,
)


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("lion", "lion"),
        ("Lion", "lion"),
        ("africa.kenya.nairobi", "africa_kenya_nairobi"),
        ("Côte d'Ivoire", "c_te_d_ivoire"),
        ("  trim me  ", "trim_me"),
        ("!@#$%", "_"),
        ("", "_"),
        ("123abc", "123abc"),
    ],
)
def test_sanitize_choice_value(raw, expected):
    assert sanitize_choice_value(raw) == expected


def test_shorten_leaves_values_up_to_100_unchanged():
    assert shorten_choice_value("a" * 100) == "a" * 100


def test_shorten_hashes_values_over_100_to_exactly_100():
    raw = "b" * 150
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:8]
    out = shorten_choice_value(raw)
    assert out == raw[:91] + "_" + digest
    assert len(out) == CHOICE_VALUE_MAX_LEN


def test_choice_value_for_option_key_sanitizes_then_shortens():
    raw = "Long.Key." * 20  # 180 chars before sanitizing
    assert choice_value_for_option_key(raw) == shorten_choice_value(sanitize_choice_value(raw))


def test_resolve_exact_match_wins_over_sanitized_match():
    # "lion" is both an exact key and the sanitized form of "Lion".
    assert resolve_option_key(["Lion", "lion"], "lion") == "lion"


def test_resolve_case_folded_key():
    assert resolve_option_key(["Lion", "Elephant"], "lion") == "Lion"


def test_resolve_tree_dotted_path():
    keys = ["natural", "natural.disease", "natural.oldage"]
    assert resolve_option_key(keys, "natural_disease") == "natural.disease"


def test_resolve_hash_shortened_long_key():
    long_key = "Very.Long.Option." * 10  # > 100 chars
    value = choice_value_for_option_key(long_key)
    assert resolve_option_key(["short", long_key], value) == long_key


def test_resolve_raises_when_nothing_matches():
    with pytest.raises(UnresolvableOptionKey):
        resolve_option_key(["healthy", "injured"], "dead")


def test_resolve_raises_on_collision():
    with pytest.raises(AmbiguousOptionKey):
        resolve_option_key(["Lion", "LION"], "lion")


def test_resolve_rejects_non_string_value():
    with pytest.raises(UnresolvableOptionKey):
        resolve_option_key(["0", "1"], 0)


def test_exceptions_share_a_base():
    assert issubclass(UnresolvableOptionKey, OptionKeyResolutionError)
    assert issubclass(AmbiguousOptionKey, OptionKeyResolutionError)
    assert issubclass(OptionKeyResolutionError, ValueError)
