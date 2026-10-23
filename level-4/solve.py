from pathlib import Path

# (row, col) step in the character grid for each emitter direction
DIRS = [
    (0, 2),    # 1 →
    (1, 1),    # 2 ↘
    (1, -1),   # 3 ↙
    (0, -2),   # 4 ←
    (-1, -1),  # 5 ↖
    (-1, 1),   # 6 ↗
]


def empty_board(r):
    rows = []
    for i in range(2 * r + 1):
        d = abs(i - r)
        n = 2 * r + 1 - d
        if d == r:
            cells = ["*"] * n
        else:
            cells = ["*"] + ["O"] * (n - 2) + ["*"]
        pad = "-" * d
        rows.append(list(pad + "-".join(cells) + pad))
    return rows


def border_ring(r):
    """Border cells in clockwise order, starting at the left corner (emitter 1)."""
    ring = []
    ring += [(r - k, k) for k in range(r)]                  # left corner -> top-left
    ring += [(0, r + 2 * k) for k in range(r)]              # top-left -> top-right
    ring += [(k, 3 * r + k) for k in range(r)]              # top-right -> right
    ring += [(r + k, 4 * r - k) for k in range(r)]          # right -> bottom-right
    ring += [(2 * r, 3 * r - 2 * k) for k in range(r)]      # bottom-right -> bottom-left
    ring += [(2 * r - k, r - k) for k in range(r)]          # bottom-left -> left
    return ring


def simulate(r, program):
    grid = empty_board(r)
    ring = border_ring(r)
    size = len(ring)
    # emitter i starts at corner i (corners are every r steps along the ring)
    pos = [i * r for i in range(6)]
    active = [False] * 6

    for line in program:
        for i, op in enumerate(line):
            if op == "F":
                pos[i] = (pos[i] + 1) % size
            elif op == "B":
                pos[i] = (pos[i] - 1) % size
            elif op == "T":
                active[i] = not active[i]

        hits = {}
        for i in range(6):
            if not active[i]:
                continue
            dr, dc = DIRS[i]
            r2, c2 = ring[pos[i]]
            r2, c2 = r2 + dr, c2 + dc
            while 0 <= r2 < len(grid) and 0 <= c2 < len(grid[r2]):
                if grid[r2][c2] in "OM":
                    hits[(r2, c2)] = hits.get((r2, c2), 0) + 1
                r2, c2 = r2 + dr, c2 + dc
        for (rr, cc), n in hits.items():
            if n == 2:
                grid[rr][cc] = "M"
            elif n >= 3:
                grid[rr][cc] = "O"

    return "\n".join("".join(row) for row in grid)


def solve(text):
    tokens = text.split()
    idx = 0
    n = int(tokens[idx]); idx += 1
    out = []
    for _ in range(n):
        r = int(tokens[idx]); idx += 1
        lines = int(tokens[idx]); idx += 1
        program = []
        for _ in range(lines):
            program.append(tokens[idx:idx + 6])
            idx += 6
        out.append(simulate(r, program) + "\n\n")
    return "".join(out)


def main():
    folder = Path(__file__).parent
    for inp in sorted(folder.glob("in_level-4_*.txt")):
        if inp.name.startswith("._"):
            continue
        out = folder / inp.name.replace("in_", "out_", 1)
        result = solve(inp.read_text())
        if out.exists() and "example" in inp.name:
            ok = result == out.read_text()
            print(f"{inp.name}: example {'OK' if ok else 'MISMATCH'}")
            if not ok:
                print(result)
            continue
        out.write_text(result)
        print(f"{inp.name} -> {out.name}")


if __name__ == "__main__":
    main()
