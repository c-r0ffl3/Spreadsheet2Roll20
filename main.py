import argparse
from processor import process


def main():
    parser = argparse.ArgumentParser(description="Make Roll20-compatible character sheet from given .html file.")
    parser.add_argument('--filename', type=str, default="input/sheet.html")

    args = parser.parse_args()
    process(args.filename)


if __name__ == '__main__':
    main()

