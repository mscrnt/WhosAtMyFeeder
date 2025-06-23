import os
import sys
import sqlite3
import types
import tempfile

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import queries


def setup_birdnames_db(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE birdnames (scientific_name TEXT PRIMARY KEY, common_name TEXT NOT NULL)")
    cur.execute("INSERT INTO birdnames VALUES ('passer domesticus', 'House Sparrow')")
    conn.commit()
    conn.close()


def setup_detections_db(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detection_time TIMESTAMP NOT NULL,
            detection_index INTEGER,
            score REAL,
            display_name TEXT,
            category_name TEXT,
            frigate_event TEXT,
            camera_name TEXT
        )
        """
    )
    cur.execute(
        "INSERT INTO detections (detection_time, detection_index, score, display_name, category_name, frigate_event, camera_name) "
        "VALUES ('2024-01-01 00:00:00', 1, 0.9, 'passer domesticus', 'bird', 'event1', 'cam')"
    )
    conn.commit()
    conn.close()


def test_get_common_name(tmp_path, monkeypatch):
    db = tmp_path / "names.db"
    setup_birdnames_db(db)
    monkeypatch.setattr(queries, "NAMEDBPATH", str(db))
    assert queries.get_common_name("passer domesticus") == "House Sparrow"


def test_recent_detections(tmp_path, monkeypatch):
    data_db = tmp_path / "detections.db"
    names_db = tmp_path / "names.db"
    setup_detections_db(data_db)
    setup_birdnames_db(names_db)
    monkeypatch.setattr(queries, "DBPATH", str(data_db))
    monkeypatch.setattr(queries, "NAMEDBPATH", str(names_db))
    res = queries.recent_detections(1)
    assert len(res) == 1
    det = res[0]
    assert det["display_name"] == "passer domesticus"
    assert det["common_name"] == "House Sparrow"
