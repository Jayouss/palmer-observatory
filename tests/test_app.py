from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_default_filters_and_export():
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=45).run()
    assert not app.exception
    assert app.metric[0].value == '344'
    assert app.metric[1].value == '3'
    assert app.metric[3].value == '99.4%'
    assert len(app.get('plotly_chart')) == 5
    assert len(app.get('download_button')) == 1
    app.multiselect[0].set_value(['Gentoo']).run()
    assert not app.exception
    assert app.metric[0].value == '124'
    app.checkbox[0].check().run()
    assert not app.exception
    assert app.metric[0].value == '123'
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert app.metric[0].value == '0'
    assert len(app.get('plotly_chart')) == 0
    app.button[0].click().run()
    assert not app.exception
    assert app.metric[0].value == '344'
    assert not app.checkbox[0].value
    assert app.slider[0].value == (2007, 2009)
    assert len(app.get('plotly_chart')) == 5
