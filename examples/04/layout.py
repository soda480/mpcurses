
screen_layout = {
    'total': {
        'position': (1, 6),
        'text': 'Total:',
        'text_color': 0,
        'color': 15,
        'regex': r'^(?P<value>\d+) total items$'
    },
    'pass': {
        'position': (2, 7),
        'text': 'Pass:',
        'text_color': 0,
        'color': 2,
        'keep_count': True,
        'regex': r'^item ".*" was processed$'
    },
    'warn': {
        'position': (3, 7),
        'text': 'Warn:',
        'text_color': 0,
        'color': 3, # 232,
        'keep_count': True,
        'regex': r'^warning processing item ".*"$'
    },
    'fail': {
        'position': (4, 7),
        'text': 'Fail:',
        'text_color': 0,
        'color': 1, # 237,
        'keep_count': True,
        'regex': r'^error processing item ".*"$'
    },
    'processing': {
        'position': (5, 1),
        'text': 'Processing:',
        'text_color': 0,
        'color': 14,
        'clear': True,
        'regex': r'^processing item "(?P<value>.*)"$'
    },
    'processing_done': {
        'position': (5, 1),
        'replace_text': ' ',
        'clear': True,
        'regex': r'^processing complete$'
    },
    '_counter_': {
        'position': (6, 0),
        'categories': [
            'pass',
            'warn',
            'fail'
        ],
        'counter_text': chr(9632),
        'width': 100
    }
}
