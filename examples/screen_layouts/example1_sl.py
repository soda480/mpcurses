def get_screen_layout():
    return {
        # '_screen': {
        #     # 'title': 'My cool program',
        #     'color': 235
        # },
        'total': {
            'position': (1, 9),
            'text': 'Total: 0',
            'text_color': 0,
            'color': 15,
            'regex': r'^(?P<value>\d+) total items$'
        },
        'processed': {
            'position': (2, 4),
            'text': 'Successful: -',
            'text_color': 0,
            'color': 2,
            'keep_count': True,
            'regex': r'^item ".*" was processed$'
        },
        'warnings': {
            'position': (3, 6),
            'text': 'Warnings: -',
            'text_color': 0,
            'color': 3,
            'keep_count': True,
            'regex': r'^warning processing item ".*"$'
        },
        'errors': {
            'position': (4, 8),
            'text': 'Errors: -',
            'text_color': 0,
            'color': 1,
            'keep_count': True,
            'regex': r'^error processing item ".*"$'
        },
        'processing': {
            'position': (5, 4),
            'text': 'Processing: -',
            'text_color': 0,
            'color': 14,
            'clear': True,
            'regex': r'^processing item "(?P<value>.*)"$'
        },
        'processing_done': {
            'position': (5, 4),
            'replace_text': ' ',
            'clear': True,
            'regex': r'^processing complete$'
        },
        'items_warning_header': {
            'position': (6, 2),
            'text': 'Items w/Warnings',
            'text_color': 0
        },
        'items_error_header': {
            'position': (6, 35),
            'text': 'Items w/Errors',
            'text_color': 0
        },
        'items_with_warnings': {
            'position': (6, 2),
            'list': True,
            'color': 3,
            'regex': r'^warning processing item "(?P<value>.*)"$'
        },
        'items_with_errors': {
            'position': (6, 35),
            'list': True,
            'color': 1,
            'regex': r'^error processing item "(?P<value>.*)"$'
        }

    }
