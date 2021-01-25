def get_screen_layout():
    return {
        'table': {
            'rows': 20,
            'cols': 3,
            'width': 50,
            'squash': True
        },
        '_on': {
            'position': (1, 0),
            'text': '',
            'replace_text': '>',
            'color': 14,
            'regex': r'^processing item .*$',
            'table': True
        },
        '_off': {
            'position': (1, 0),
            'text': '',
            'replace_text': ' ',
            'regex': r'^processed item .*$',
            'table': True
        },
        'vectors': {
            'position': (1, 2),
            'text': '---',
            'text_color': 244,
            'color': 7,
            'regex': r'^item .* has (?P<value>.*) vectors$',
            'table': True,
        },
        'processed': {
            'position': (1, 6),
            'text': '---',
            'text_color': 244,
            'color': 7,
            'keep_count': True,
            'regex': r'^processed vector .*$',
            'zfill': 3,
            'table': True
        },
        'version': {
            'position': (1, 10),
            'text': '-------',
            'text_color': 244,
            'color': 244,
            'width': 7,
            'right_justify': True,
            'regex': r'^item .* head is at (?P<value>.*)$',
            'table': True
        },
        'item_initialized': {
            'position': (1, 18),
            'text': '',
            'color': 244,
            'width': 28,
            'regex': r"^'item' is '(?P<value>.*)'$",
            'table': True
        },
        'item_processing': {
            'position': (1, 18),
            'text': '',
            'color': 14,
            'width': 28,
            'regex': r'^processing item (?P<value>.*)$',
            'table': True
        },
        'item_processed': {
            'position': (1, 18),
            'text': '',
            'color': 7,
            'width': 28,
            'regex': r'^processed item (?P<value>.*)$',
            'table': True
        }
    }
