from primes import count_primes
from mpcurses import MPcurses

def main():
    MPcurses(
        function=count_primes,
        process_data=[
            {'range': '1-10000'},
            {'range': '10001-20000'},
            {'range': '20001-30000'},
        ],
        screen_layout={
            'range_header': {
                'position': (2, 5), 'text': 'Range', 'text_color': 14 },
            'prime_header': {
                'position': (2, 14), 'text': 'Prime', 'text_color': 14 },
            'number': {
                'position': (3, 2), 'color': 15, 'table': True,
                'regex': r'^checking number (?P<value>\d+)$' },
            'upper': {
                'position': (3, 7), 'color': 27, 'table': True,
                'regex': r'^checking primes between \d+(?P<value>/\d+)$' },
            'prime': {
                'position': (3, 14), 'color': 2, 'table': True, 'keep_count': True, 'zfill': 4,
                'regex': r'^\d* is prime$' },
            '_counter_': {
                'position': (3, 19), 'color': 15, 'table': True, 'modulus': 125, 'counter_text': chr(9632),
                'categories': ['number'] },
            'total_header': {
                'position': (6, 7), 'text': 'Total:', 'text_color': 14 },
            'total': {
                'position': (6, 14), 'color': 2, 'keep_count': True, 'zfill': 4,
                'regex': r'^\d* is prime$' },
        }).execute()

if __name__ == '__main__':
    main()
