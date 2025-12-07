"""
Convert Clang C Abstract Syntax Tree to GML Format
"""
import argparse
import json

import pygml.ast


def main() -> None:
    cfg = parse_args()
    with open(cfg.FILE, "r") as f:
        data = json.load(f)
    prog = pygml.ast.decode_program(data)
    json2 = pygml.ast.encode_program(prog)
    
    with open(cfg.FILE + "2", "w") as f:
        json.dump(json2, f)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("FILE", type=str,
                        help="File to convert. Expects .json format!")
    cfg = parser.parse_args()
    return cfg


if __name__ == "__main__":
    main()
