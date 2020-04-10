import click
import pytest  # type: ignore

from bibo import query


def test_search_a_key_with_colon(data):
    results = list(query.search(data, ["Gurion:"]))
    assert len(results) == 1


def test_search_single_term(data):
    results = list(query.search(data, ["asimov"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "Foundation"


def test_search_multiple_search_terms(data):
    results = list(query.search(data, ["tolkien", "hobbit"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "The Hobbit"


def test_search_specific_field(data):
    results = list(query.search(data, ["year:1937"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "The Hobbit"


def test_search_specific_field_with_capital_letter(data):
    """Issue #27"""
    results = list(query.search(data, ["author:asimov"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "Foundation"


def test_search_multiple_terms_are_anded(data):
    results = list(query.search(data, ["tolkien", "type:book"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "The Hobbit"


def test_search_invalid_search_term(data):
    with pytest.raises(Exception, match="Invalid search term") as e:
        list(query.search(data, "a:b:c"))


def test_search_with_capitalized_search_term(data):
    """Issue #28"""
    results = list(query.search(data, ["ASIMOV"]))
    assert len(results) == 1
    assert results[0].entry["fields"]["title"] == "Foundation"


def test_open_multiple_entries_one_exact_match(data):
    with pytest.raises(click.ClickException):
        query.get(data, ["ab"])
    query.get(data, ["abc"])


def test_search_match_details(data):
    results = list(query.search(data, ["tolkien", "hobbit"]))
    assert len(results) == 1
    assert "tolkien" in results[0].match["key"]
    assert ("title", ["Hobbit"]) in results[0].match["fields"].items()


def test_match(data):
    entry = data[0]
    assert query._match(entry, "Tolkien") == {"key": "tolkien"}
    assert query._match(entry, "article") == {}
    assert query._match(entry, "book") == {"type": "book"}
    assert query._match(entry, "hobbit") == {
        "fields": {"title": "Hobbit", "file": "hobbit"}
    }
    assert query._match(entry, "year:193") == {"fields": {"year": "193"}}
    assert query._match(entry, "year:1937") == {"fields": {"year": "1937"}}


def test_update_result():
    entry = {
        "a": "1234",
        "props": {"b": "ABCD"},
    }
    r1 = query.SearchResult(entry, {})
    assert query._update_result(r1, {}) == None

    r2 = query._update_result(r1, {"a": "1"})
    assert "a" in r2.match
    assert r2.match["a"] == ["1"]

    r3 = query._update_result(r2, {"props": {"b": "ABC"}})
    assert r3.match["props"]["b"] == ["ABC"]

    r4 = query._update_result(r3, {"props": {"b": "D"}})
    assert r3.match["props"]["b"] == ["ABC", "D"]


def test_nested_append():
    d = {"x": {"y": ["z"]}}
    u = {"x": {"y": "t"}}
    assert query._nested_append(d, u) == {"x": {"y": ["z", "t"]}}

    d = {}
    u = {"x": "X"}
    assert query._nested_append(d, u) == {"x": ["X"]}
