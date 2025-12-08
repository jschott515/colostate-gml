"""
Util for cleaning up clang ast - make more readable for developement
"""
import json
import sys
from typing import Any

FORBIDDEN = ("id", "loc", "range", "mangledname", "isused", "type", "valueCategory", "castKind")


def filter_node(node: Any) -> Any:
    """Recursively filter forbidden keys from json structures."""

    if isinstance(node, dict):
        new = {}
        for k, v in node.items():
            # remove any key containing any forbidden substring
            if any(f in k.lower() for f in FORBIDDEN):
                continue
            new[k] = filter_node(v)
        return new

    elif isinstance(node, list):
        return [filter_node(v) for v in node]

    else:
        return node


def main():
    if len(sys.argv) != 3:
        print("Usage: filter_ast.py input.json output.json")
        sys.exit(1)

    inp, out = sys.argv[1], sys.argv[2]

    with open(inp, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned = filter_node(data)

    with open(out, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"Filtered JSON written to {out}")


if __name__ == "__main__":
    main()
