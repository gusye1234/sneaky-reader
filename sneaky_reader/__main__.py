import os
import pickle
import argparse
from .reader import TxtBrowser, Reader


def commandline():
    parser = argparse.ArgumentParser(
        prog='Sneaky-Reader',
        description='undercover book-reader in your terminal',
        epilog='Text at the bottom of help')
    parser.add_argument('-p', '--path', default="",
                        type=str, help="Path to your TXT book")
    parser.add_argument('-e', '--re', default="",
                        type=str, help="Regular Expression to split your txt!")
    parser.add_argument('-l', '--list', action="store_true",
                        help="Show all cached books")
    parser.add_argument('-b', '--book', default=-1, type=int,
                        help="Pick the book from the cached list(use `-l` to look the list)")
    return parser.parse_args()


def get_root_dir():
    return os.path.dirname(os.path.dirname(__file__))


def get_cache_dir():
    root = get_root_dir()
    cache_dir = os.path.join(root, "book_cache")
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    return cache_dir


def get_cache_path(book_path):
    parent = get_cache_dir()
    name = os.path.basename(book_path).split(".")[0]
    cache_name = f"sneak_reader_{name}.pkl"
    return os.path.join(parent, cache_name)


def get_cache_books():
    parent = get_cache_dir()
    files = os.listdir(parent)
    files = [f for f in files if f.endswith(
        ".pkl") and f.startswith("sneak_reader_")]
    files = [os.path.join(parent, f) for f in files]
    files = sorted(files)
    return files


def print_cache_name():
    files = get_cache_books()
    files = [os.path.basename(f) for f in files]
    books = [f.replace("sneak_reader_", '').replace(".pkl", '')
             for f in files]
    for i, b in enumerate(books):
        print(f"[{i}] {b}")


if __name__ == "__main__":
    args = commandline()
    if args.list:
        print_cache_name()
        exit()
    if args.book != -1:
        book_paths = get_cache_books()
        assert 0 <= args.book <= len(
            book_paths), f"Wrong index for book, expected in [0, {len(book_paths)}]"
        cache_path = book_paths[args.book]
    else:
        assert args.path != "", "Must input your book path"
        cache_path = get_cache_path(args.path)

    if os.path.exists(cache_path):
        try:
            reader = Reader.from_pkl(cache_path)
        except TypeError:
            raise TypeError(
                f"Wrong cache format from {cache_path}, delete it then try again")
        except FileNotFoundError:
            with open(cache_path, 'rb') as f:
                file_name = pickle.load(f)["txt"]
            raise FileNotFoundError(
                f"Expect a TXT file in {file_name}, but found none!")
    else:
        if args.re == "":
            raise ValueError("Import a new book must set your `-e`")
        reader = Reader(args.path, args.re)
    TxtBrowser(reader=reader, save_path=cache_path).run()
