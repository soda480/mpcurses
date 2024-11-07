screen_layout = {
    'range_header': {
        'position': (2, 5), 'text': 'Range', 'text_color': 14 },
    'prime_header': {
        'position': (2, 14), 'text': 'Prime', 'text_color': 14 },
    'number': {
        'position': (3, 2), 'color': 15, 'zfill': 5,
        'regex': r'^checking number (?P<value>\d+)$' },
    'upper': {
        'position': (3, 7), 'color': 27,
        'regex': r'^checking primes between \d+(?P<value>/\d+)$' },
    'prime': {
        'position': (3, 14), 'color': 2, 'keep_count': True, 'zfill': 4,
        'regex': r'^\d* is prime$' }
}
