import sqlite3
import sys
import types
import importlib

def test_setupdb_creates_table(tmp_path, monkeypatch):
    db_path = tmp_path / "speciesid.db"

    # Create stub modules for missing dependencies
    sys.modules.setdefault('numpy', types.ModuleType('numpy'))
    sys.modules.setdefault('cv2', types.ModuleType('cv2'))
    tflite_module = types.ModuleType('tflite_support')
    task_module = types.ModuleType('task')
    task_module.core = types.ModuleType('core')
    task_module.processor = types.ModuleType('processor')
    task_module.vision = types.ModuleType('vision')
    tflite_module.task = task_module
    sys.modules.setdefault('tflite_support', tflite_module)
    sys.modules.setdefault('tflite_support.task', task_module)
    sys.modules.setdefault('tflite_support.task.core', task_module.core)
    sys.modules.setdefault('tflite_support.task.processor', task_module.processor)
    sys.modules.setdefault('tflite_support.task.vision', task_module.vision)
    sys.modules.setdefault('paho', types.ModuleType('paho'))
    mqtt_pkg = types.ModuleType('paho.mqtt')
    client_mod = types.ModuleType('paho.mqtt.client')
    client_mod.Client = lambda *args, **kwargs: None
    mqtt_pkg.client = client_mod
    sys.modules.setdefault('paho.mqtt', mqtt_pkg)
    sys.modules.setdefault('paho.mqtt.client', client_mod)
    flask_mod = types.ModuleType('flask')
    class DummyFlask(types.SimpleNamespace):
        def __init__(self, *args, **kwargs):
            super().__init__(route=lambda *a, **k: (lambda f: f))
            self.jinja_env = types.SimpleNamespace(filters={})

    flask_mod.Flask = DummyFlask
    flask_mod.render_template = lambda *a, **k: ""
    flask_mod.request = None
    flask_mod.redirect = lambda *a, **k: ""
    flask_mod.url_for = lambda *a, **k: ""
    flask_mod.send_file = lambda *a, **k: None
    flask_mod.abort = lambda *a, **k: None
    flask_mod.send_from_directory = lambda *a, **k: None
    flask_mod.jsonify = lambda *a, **k: {}
    sys.modules.setdefault('flask', flask_mod)
    yaml_mod = types.ModuleType('yaml')
    yaml_mod.safe_load = lambda f: {}
    sys.modules.setdefault('yaml', yaml_mod)
    sys.modules.setdefault('requests', types.ModuleType('requests'))
    sys.modules.setdefault('PIL', types.ModuleType('PIL'))
    sys.modules.setdefault('PIL.Image', types.ModuleType('Image'))
    sys.modules.setdefault('PIL.ImageOps', types.ModuleType('ImageOps'))

    speciesid = importlib.import_module('speciesid')
    monkeypatch.setattr(speciesid, 'DBPATH', str(db_path))
    speciesid.setupdb()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detections'")
    assert cur.fetchone() is not None
