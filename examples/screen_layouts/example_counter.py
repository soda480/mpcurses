
def get_screen_layout():
    return {
        'total': {
            'position': (1, 9),
            'text': 'Total: 0',
            'text_color': 0,
            'color': 15,
            'regex': r'^(?P<value>\d+) total items$'
        },
        'successful': {
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
            'color': 3, # 232,
            'keep_count': True,
            'regex': r'^warning processing item ".*"$'
        },
        'errors': {
            'position': (4, 8),
            'text': 'Errors: -',
            'text_color': 0,
            'color': 1, # 237,
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
        '_counter_': {
            'position': (6, 0),
            'categories': [
                'successful',
                'warnings',
                'errors'
            ],
            'counter_text': '|',
            'width': 100
        }
    }
