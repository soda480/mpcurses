screen_layout = {
    'table': {
        'orientation': 'horizontal',
        'padding': 5
    },
    'header_group': {
        'position': (1, 9),
        'text': 'Group:',
        'text_color': 0
    },
    'header_total': {
        'position': (2, 9),
        'text': 'Total:',
        'text_color': 0
    },
    'header_processed': {
        'position': (3, 4),
        'text': 'Successful:',
        'text_color': 0
    },
    'header_warnings': {
        'position': (4, 6),
        'text': 'Warnings:',
        'text_color': 0
    },
    'header_errors': {
        'position': (5, 8),
        'text': 'Errors:',
        'text_color': 0
    },
    'group': {
        'position': (1, 18),
        'text': '--',
        'text_color': 0,
        'color': 14,
        'regex': r"^group(?P<value>.*) has \d+ total items$",
        'table': True
    },
    'total': {
        'position': (2, 16),
        'text': '----',
        'text_color': 0,
        'color': 15,
        'regex': r"^group.* has (?P<value>\d+) total items$",
        'table': True
    },
    'successful': {
        'position': (3, 17),
        'text': '---',
        'text_color': 0,
        'color': 2,
        'keep_count': True,
        'regex': r'^item ".*" was processed$',
        'table': True,
    },
    'warnings': {
        'position': (4, 17),
        'text': '---',
        'text_color': 0,
        'color': 3,
        'keep_count': True,
        'regex': r'^warning processing item ".*"$',
        'table': True,
    },
    'errors': {
        'position': (5, 17),
        'text': '---',
        'text_color': 0,
        'color': 1,
        'keep_count': True,
        'regex': r'^error processing item ".*"$',
        'table': True,
    },
    'item': {
        'position': (7, 2),
        'color': 14,
        'clear': True,
        'padding': 33,
        'regex': r'^processing item "group\d+-(?P<value>.*)"$',
        'table': True,
    },
    'item_clear': {
        'position': (7, 2),
        'replace_text': ' ',
        'clear': True,
        'regex': r'^processing complete for group.*$',
        # 'table': True,
    },
    'group01_items_header': {
        'position': (8, 2),
        'text': 'group01 Warnings/Errors',
        'text_color': 0
    },
    'group02_items_header': {
        'position': (8, 35),
        'text': 'group02 Warnings/Errors',
        'text_color': 0
    },
    'group03_items_header': {
        'position': (8, 68),
        'text': 'group03 Warnings/Errors',
        'text_color': 0
    },
    'group01_items': {
        'position': (8, 2),
        'list': True,
        'color': 3,
        'regex': r'^(warning|error) processing item "group01-(?P<value>.*)"$',
        'effects': [
            {
                'regex': r'^error processing item .*$',
                'color': 1
            }, {
                'regex': r'^warning processing item .*$',
                'color': 3
            }
        ]
    },
    'group02_items': {
        'position': (8, 35),
        'list': True,
        'color': 3,
        'regex': r'^(warning|error) processing item "group02-(?P<value>.*)"$',
        'effects': [
            {
                'regex': r'^error processing item .*$',
                'color': 1
            }, {
                'regex': r'^warning processing item .*$',
                'color': 3
            }
        ]
    },
    'group03_items': {
        'position': (8, 68),
        'list': True,
        'color': 3,
        'regex': r'^(warning|error) processing item "group03-(?P<value>.*)"$',
        'effects': [
            {
                'regex': r'^error processing item .*$',
                'color': 1
            }, {
                'regex': r'^warning processing item .*$',
                'color': 3
            }
        ]
    },
}
