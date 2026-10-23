from pathlib import Path

# (row, col) step in the character grid for each emitter direction
DIRS = {
    "1": (0, 2),    # →
    "2": (1, 1),    # ↘
    "3": (1, -1),   # ↙
    "4": (0, -2),   # ←
    "5": (-1, -1),  # ↖
    "6": (-1, 1),   # ↗
}


def fire(grid):
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch in DIRS:
                dr, dc = DIRS[ch]
                r2, c2 = r + dr, c + dc
                while 0 <= r2 < len(grid) and 0 <= c2 < len(grid[r2]):
                    if grid[r2][c2] == "O":
                        grid[r2][c2] = "M"
                    r2, c2 = r2 + dr, c2 + dc
                return


def solve(text):
    lines = text.splitlines()
    n = int(lines[0])
    i = 1
    out = []
    for _ in range(n):
        while not lines[i].strip():
            i += 1
        rows = int(lines[i].split()[1])
        grid = [list(line) for line in lines[i + 1:i + 1 + rows]]
        i += 1 + rows
        fire(grid)
        out.append("\n".join("".join(row) for row in grid) + "\n\n")
    return "".join(out)


def main():
    folder = Path(__file__).parent
    for inp in sorted(folder.glob("in_level-2_*.txt")):
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
