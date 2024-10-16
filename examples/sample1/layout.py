screen_layout = {
    'range_header': { 'position': (2, 5), 'text': 'Range', 'text_color': 14 },
    'prime_header': { 'position': (2, 14), 'text': 'Prime', 'text_color': 14 },
    'number': { 'position': (3, 2), 'color': 15, 'table': True, 'regex': r'^checking (?P<value>\d+)/\d+$' },
    'upper': { 'position': (3, 7), 'color': 27, 'table': True, 'regex': r'^checking \d+(?P<value>/\d+)$' },
    'prime': { 'position': (3, 14), 'color': 2, 'keep_count': True, 'zfill': 4, 'table': True, 'regex': r'^\d* is prime$' },
    '_counter_': { 'position': (3, 19), 'color': 15, 'table': True, 'modulus': 200, 'counter_text': chr(9632), 'categories': ['number'] },
    'total_header': { 'position': (6, 7), 'text': 'Total:', 'text_color': 14 },
    'total': { 'position': (6, 14), 'color': 2, 'keep_count': True, 'zfill': 4, 'regex': r'^\d* is prime$' },
}
