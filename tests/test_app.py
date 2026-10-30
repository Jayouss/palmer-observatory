from pathlib import Path
from html.parser import HTMLParser
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def rendered_statistics(app):
    class StatisticsParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.current = None
            self.values = {}

        def handle_starttag(self, tag, attrs):
            if tag == 'strong':
                self.current = dict(attrs).get('data-stat')

        def handle_endtag(self, tag):
            if tag == 'strong':
                self.current = None

        def handle_data(self, data):
            if self.current:
                self.values[self.current] = self.values.get(self.current, '') + data

    parser = StatisticsParser()
    for element in app.get('html'):
        parser.feed(element.proto.body)
    return parser.values


def test_dashboard_default_filters_and_export():
    app = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=45).run()
    assert not app.exception
    assert rendered_statistics(app) == {'observations': '344', 'species': '3',
                                         'mass': '4,202 g', 'quality': '99.4%'}
    assert len(app.get('plotly_chart')) == 5
    assert len(app.get('download_button')) == 1
    app.multiselect[0].set_value(['Gentoo']).run()
    assert not app.exception
    assert rendered_statistics(app)['observations'] == '124'
    app.checkbox[0].check().run()
    assert not app.exception
    assert rendered_statistics(app)['observations'] == '123'
    app.multiselect[0].set_value([]).run()
    assert not app.exception
    assert rendered_statistics(app) == {'observations': '0', 'species': '0',
                                         'mass': '-', 'quality': '-'}
    assert len(app.get('plotly_chart')) == 0
    app.button[0].click().run()
    assert not app.exception
    assert rendered_statistics(app)['observations'] == '344'
    assert not app.checkbox[0].value
    assert app.slider[0].value == (2007, 2009)
    assert len(app.get('plotly_chart')) == 5
