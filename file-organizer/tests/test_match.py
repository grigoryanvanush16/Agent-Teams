import yaml
from router.match import load_manifest, match_file

MANIFEST = [
    {"name": "tz_dwh", "dest": "/x/tz", "keywords": [r"^тз ", r"^тз_"]},
    {"name": "renewals", "dest": "/x/ren", "keywords": [r"продлени"]},
]


def test_match_by_prefix_keyword():
    assert match_file("ТЗ Отчет по опозданиям.docx", MANIFEST)["name"] == "tz_dwh"


def test_match_is_case_insensitive():
    assert match_file("Сравнение_продления.xlsx", MANIFEST)["name"] == "renewals"


def test_no_match_returns_none():
    assert match_file("Портрет.xlsx", MANIFEST) is None


def test_order_is_priority():
    manifest = [
        {"name": "narrow", "dest": "/a", "keywords": [r"отчет продажи"]},
        {"name": "broad", "dest": "/b", "keywords": [r"отчет"]},
    ]
    assert match_file("Отчет продажи 2.0.xlsx", manifest)["name"] == "narrow"


def test_load_manifest_roundtrip(tmp_path):
    f = tmp_path / "m.yaml"
    f.write_text(yaml.safe_dump(MANIFEST, allow_unicode=True), encoding="utf-8")
    loaded = load_manifest(f)
    assert loaded[0]["name"] == "tz_dwh"


def test_load_missing_manifest_returns_empty(tmp_path):
    assert load_manifest(tmp_path / "nope.yaml") == []
