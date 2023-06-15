import os
import pickle
import argparse
from .reader import TxtBrowser, Reader


def commandline():
    parser = argparse.ArgumentParser(
                    prog='Sneaky-Reader',
                    description='undercover book-reader in your terminal',
                    epilog='Text at the bottom of help')
    parser.add_argument('-p', '--path', required=True,
                        type=str, help="Path to your TXT book")
    parser.add_argument('-e', '--re', required=True,
                        type=str, help="Regular Expression to split your txt!")
    return parser.parse_args()

def get_cache_path(book_path):
    partent = os.path.dirname(book_path)
    name = os.path.basename(book_path).split(".")[0]
    cache_name = f"sneak_reader_{name}.pkl"
    return os.path.join(partent, cache_name)

if __name__ == "__main__":
    args = commandline()
    cache_path = get_cache_path(args.path)
    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            reader = pickle.load(f)
    else:
        reader = Reader(args.path, args.re)
    TxtBrowser(reader=reader, save_path=cache_path).run()