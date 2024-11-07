screen_layout = {
    'number_header': {
        'position': (2, 4),
        'text': 'Number',
        'text_color': 14,
    },
    'prime_header': {
        'position': (2, 15),
        'text': 'Prime :',
        'text_color': 14,
    },
    'not_prime_header1': {
        'position': (1, 22),
        'text': 'Not',
        'text_color': 14,
    },
    'not_prime_header2': {
        'position': (2, 21),
        'text': 'Prime',
        'text_color': 14,
    },
    'number': {
        'position': (3, 1),
        'text': '',
        'color': 27,
        'regex': '^checking (?P<value>\d+)/\d+$',
        'table': True
    },
    'uppper_number': {
        'position': (3, 7),
        'text': '',
        'color': 15,
        'regex': '^checking \d+(?P<value>/\d+)$',
        'table': True
    },
    'prime': {
        'position': (3, 15),
        'text': '',
        'color': 2,
        'keep_count': True,
        'zfill': 5,
        'regex': '^prime$',
        'table': True
    },
    'not_prime': {
        'position': (3, 21),
        'text': '',
        'color': 3,
        'keep_count': True,
        'regex': '^not prime$',
        'zfill': 5,
        'table': True
    },
    '_counter_': {
        'position': (3, 27),
        'categories': [
            'number'
        ],
        'counter_text': '|',
        'modulus': 200,
        'color': 15,
        # 'regex': '^total of (?P<value>\d+) numbers$',
        'table': True
    },
    'total_header': {
        'position': (14, 8),
        'text': 'Total:',
        'text_color': 14,
    },
    'prime_total': {
        'position': (14, 15),
        'text': '',
        'color': 2,
        'keep_count': True,
        'zfill': 5,
        'regex': '^prime$',
    },
    'not_prime_total': {
        'position': (14, 21),
        'text': '',
        'color': 3,
        'keep_count': True,
        'zfill': 5,
        'regex': '^not prime$',
    },
}
