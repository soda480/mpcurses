def get_screen_layout():
    return {
        'number': {
            'position': (1, 4),
            'text': 'Number: -',
            'text_color': 7,
            'color': 27,
            'clear': True,
            'regex': r'^checking (?P<value>\d+)$'
        },
        'prime': {
            'position': (2, 4),
            'text': 'Primes: 0',
            'text_color': 7,
            'color': 2,
            'keep_count': True,
            'zfill': 4,
            'regex': '^prime$'
        },
        'not_prime': {
            'position': (3, 0),
            'text': 'Not Primes: 0',
            'text_color': 7,
            'color': 3,
            'keep_count': True,
            'zfill': 4,
            'regex': '^not prime$'
        }
    }
