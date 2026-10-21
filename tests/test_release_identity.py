from pathlib import Path
import json

from streamlit.testing.v1 import AppTest


def test_public_release_identity_and_scientific_boundary():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py'), default_timeout=30).run()
    assert not app.exception
    assert any('Versão 0.2.0' in caption.value for caption in app.caption)
    assert any('sujeitas à validação' in caption.value for caption in app.caption)
    marker = json.loads((Path(__file__).resolve().parents[1] / 'static/release.json').read_text(encoding='utf-8'))
    assert marker['version'] == '0.2.0'
    assert marker['experimental_recommendations_validated'] is False
