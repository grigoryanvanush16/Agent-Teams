import yaml

import file_router


def _setup(tmp_path):
    src = tmp_path / "Downloads"
    src.mkdir()
    dest = tmp_path / "Продления"
    unsorted = tmp_path / "_не_разобрано"
    journal = tmp_path / "journal.jsonl"

    (src / "Сравнение_продления.xlsx").write_text("a")
    (src / "Портрет.xlsx").write_text("b")  # ни одно правило не ловит

    config = tmp_path / "config.yaml"
    config.write_text(yaml.safe_dump({
        "sources": [str(src)],
        "unsorted_dir": str(unsorted),
        "journal": str(journal),
        "min_age_seconds": 0,
    }, allow_unicode=True), encoding="utf-8")

    manifest = tmp_path / "projects.yaml"
    manifest.write_text(yaml.safe_dump([
        {"name": "renewals", "dest": str(dest), "keywords": ["продлени"]},
    ], allow_unicode=True), encoding="utf-8")

    return src, dest, unsorted, config, manifest, journal


def test_dry_run_moves_nothing(tmp_path):
    src, dest, unsorted, config, manifest, journal = _setup(tmp_path)
    file_router.main(["--dry-run", "--config", str(config),
                      "--manifest", str(manifest)])
    assert (src / "Сравнение_продления.xlsx").exists()
    assert not dest.exists()
    assert not journal.exists()


def test_real_run_routes_matched_and_unsorted(tmp_path):
    src, dest, unsorted, config, manifest, journal = _setup(tmp_path)
    file_router.main(["--config", str(config), "--manifest", str(manifest)])
    assert (dest / "Сравнение_продления.xlsx").exists()
    assert (unsorted / "Портрет.xlsx").exists()
    assert not (src / "Сравнение_продления.xlsx").exists()
    assert journal.exists()


def test_undo_after_run_restores(tmp_path):
    src, dest, unsorted, config, manifest, journal = _setup(tmp_path)
    file_router.main(["--config", str(config), "--manifest", str(manifest)])
    file_router.main(["--undo", "--config", str(config),
                      "--manifest", str(manifest)])
    assert (src / "Сравнение_продления.xlsx").exists()
    assert (src / "Портрет.xlsx").exists()
