"""
Convert Clang C Abstract Syntax Tree to GML Format
"""
import argparse
import json
import typing

import pygml.ast


def main() -> None:
    cfg = parse_args()
    file = typing.cast(str, cfg.FILE)

    with open(file, "r") as f:
        data = json.load(f)
    prog = pygml.ast.convert_program(data)
    conv = pygml.ast.encode_program(prog)

    with open(file + ".conv", "w") as f:
        json.dump(conv, f)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("FILE", type=str,
                        help="File to convert. Expects .json format!")
    cfg = parser.parse_args()
    return cfg


if __name__ == "__main__":
    main()
