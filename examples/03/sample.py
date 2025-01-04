from primes import count_primes
from layout import screen_layout
from mpcurses import MPcurses

def main():
    MPcurses(
        function=count_primes,
        process_data=[
            {'nrange': '00001-10000'},
            {'nrange': '10001-20000'},
            {'nrange': '20001-30000'},
            {'nrange': '30001-40000'},
            {'nrange': '40001-50000'},
            {'nrange': '50001-60000'},
            {'nrange': '60001-70000'}],
        screen_layout=screen_layout).execute()

if __name__ == '__main__':
    main()
