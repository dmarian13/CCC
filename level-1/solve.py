import sys
from pathlib import Path


def board(r):
    rows = []
    for i in range(2 * r + 1):
        d = abs(i - r)
        n = 2 * r + 1 - d
        if d == r:
            cells = ["*"] * n
        else:
            cells = ["*"] + ["O"] * (n - 2) + ["*"]
        pad = "-" * d
        rows.append(pad + "-".join(cells) + pad)
    return "\n".join(rows)


def solve(text):
    nums = list(map(int, text.split()))
    n, radii = nums[0], nums[1:]
    return "".join(board(r) + "\n\n" for r in radii[:n])


def main():
    folder = Path(__file__).parent
    for inp in sorted(folder.glob("in_level-1_*.txt")):
        if inp.name.startswith("._"):
            continue
        out = folder / inp.name.replace("in_", "out_", 1)
        result = solve(inp.read_text())
        if out.exists() and "example" in inp.name:
            ok = result == out.read_text()
            print(f"{inp.name}: example {'OK' if ok else 'MISMATCH'}")
            continue
        out.write_text(result)
        print(f"{inp.name} -> {out.name}")


if __name__ == "__main__":
    main()
