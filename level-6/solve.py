import sys
import os

DIR_TO = {
    'E':  (2, 0),
    'SE': (1, 1),
    'SW': (-1, 1),
    'W':  (-2, 0),
    'NW': (-1, -1),
    'NE': (1, -1),
}

FIRE_OV = [
    (2, 0),   # Track 0: E
    (1, 1),   # Track 1: SE
    (-1, 1),  # Track 2: SW
    (-2, 0),  # Track 3: W
    (-1, -1), # Track 4: NW
    (1, -1),  # Track 5: NE
]

class BoardGeometry:
    def __init__(self, board_radius):
        self.radius = board_radius + 1
        self.cols = 4 * self.radius - 3
        self.rows = 2 * self.radius - 1
        self._build_perimeter()
        self._build_rays()

    def _is_in_grid(self, c, r):
        if r < 0 or r >= 2 * self.radius - 1:
            return False
        if (r + c + self.radius + 1) % 2 != 0:
            return False
        if r < self.radius:
            return c + r >= self.radius - 1 and c - r <= self.cols - self.radius + 1
        return c + (2 * self.radius - 1 - r) >= self.radius - 1 and c + r - 2 * self.radius + 1 < self.cols - self.radius + 1

    def _build_perimeter(self):
        perimeter = []
        if self.radius > 1:
            cur = [0, self.radius - 1]
            for d in ['NE', 'E', 'SE', 'SW', 'W', 'NW']:
                dc, dr = DIR_TO[d]
                for _ in range(self.radius - 1):
                    perimeter.append((cur[0], cur[1]))
                    cur[0] += dc
                    cur[1] += dr
        self.perimeter = perimeter
        self.perim_len = len(perimeter)

    def _build_rays(self):
        self.cell_to_perim = {}
        for p_idx, (c_ov, r_ov) in enumerate(self.perimeter):
            for t, (dc, dr) in enumerate(FIRE_OV):
                ec, er = c_ov + dc, r_ov + dr
                while self._is_in_grid(ec, er):
                    self.cell_to_perim[(er, ec, t)] = p_idx
                    ec += dc
                    er += dr

def parse_input_file(filepath):
    with open(filepath, 'r') as f:
        lines = [line.rstrip('\r\n') for line in f]
    num_tests = int(lines[0].strip())
    idx = 1
    tests = []
    for _ in range(num_tests):
        while idx < len(lines) and not lines[idx].strip():
            idx += 1
        if idx >= len(lines):
            break
        parts = lines[idx].strip().split()
        b_rad, p_rows, p_cols, p_count = map(int, parts)
        idx += 1
        p_grid = []
        for _ in range(p_rows):
            p_grid.append(list(lines[idx]))
            idx += 1
        tests.append({
            'radius': b_rad,
            'p_rows': p_rows,
            'p_cols': p_cols,
            'count': p_count,
            'pattern': p_grid
        })
    return tests

def get_move_commands(from_pos, to_pos, perim_len):
    """Calculează cea mai scurtă serie de pași 'F' sau 'B' pe perimetru."""
    if from_pos == to_pos:
        return []
    f_dist = (to_pos - from_pos) % perim_len
    b_dist = (from_pos - to_pos) % perim_len
    if f_dist <= b_dist:
        return ['F'] * f_dist
    return ['B'] * b_dist

def solve_case(test):
    geom = BoardGeometry(test['radius'])
    perim_len = geom.perim_len
    edge_len = max(geom.radius - 1, 1)

    # Coordonatele curente pe perimetru și starea activă pentru cele 6 track-uri
    pos = [i * edge_len for i in range(6)]
    active = [False] * 6

    # Colectăm toate celulele 'M'
    matter_cells = []
    for r in range(test['p_rows']):
        for c in range(test['p_cols']):
            if test['pattern'][r][c] == 'M':
                matter_cells.append((r, c))

    tA, tB = 0, 2
    program = []

    def emit(cmds):
        for c in cmds:
            program.append(" ".join(c))

    # Pre-ordonare inițială a celulelor prin Nearest-Neighbor pentru a minimiza traversarea
    ordered_cells = []
    rem = list(matter_cells)
    cur_pA = pos[tA]
    cur_pB = pos[tB]

    while rem:
        best_i = 0
        min_cost = 999999
        for i, (r, c) in enumerate(rem):
            target_pA = geom.cell_to_perim[(r, c, tA)]
            target_pB = geom.cell_to_perim[(r, c, tB)]
            cost = max(len(get_move_commands(cur_pA, target_pA, perim_len)),
                       len(get_move_commands(cur_pB, target_pB, perim_len)))
            if cost < min_cost:
                min_cost = cost
                best_i = i
        target = rem.pop(best_i)
        ordered_cells.append(target)
        cur_pA = geom.cell_to_perim[(target[0], target[1], tA)]
        cur_pB = geom.cell_to_perim[(target[0], target[1], tB)]

    # Producem modelul de test['count'] ori
    for iteration in range(test['count']):
        # Alternăm direcția de parcurgere la ciclurile impare pentru 0 cost între iterații
        cell_sequence = ordered_cells if (iteration % 2 == 0) else list(reversed(ordered_cells))

        # Activăm tB doar dacă nu este deja pornit
        if not active[tB]:
            cmd = ['-'] * 6
            cmd[tB] = 'T'
            emit([cmd])
            active[tB] = True

        for r, c in cell_sequence:
            pA = geom.cell_to_perim[(r, c, tA)]
            pB = geom.cell_to_perim[(r, c, tB)]

            movesA = get_move_commands(pos[tA], pA, perim_len)
            movesB = get_move_commands(pos[tB], pB, perim_len)
            max_moves = max(len(movesA), len(movesB))

            # Paralelizăm pașii de mișcare pentru ambii emițători
            for step_i in range(max_moves):
                cmd = ['-'] * 6
                if step_i < len(movesA):
                    cmd[tA] = movesA[step_i]
                if step_i < len(movesB):
                    cmd[tB] = movesB[step_i]
                emit([cmd])

            pos[tA] = pA
            pos[tB] = pB

            # Impuls rapid de scânteie pentru sinteza celulei M
            cmd_on = ['-'] * 6
            cmd_on[tA] = 'T'
            cmd_off = ['-'] * 6
            cmd_off[tA] = 'T'
            emit([cmd_on, cmd_off])

        # La finalul iterației, stingem tB pentru validarea pattern-ului dacă nu mai urmează puncte
        if iteration == test['count'] - 1:
            cmd = ['-'] * 6
            cmd[tB] = 'T'
            emit([cmd])
            active[tB] = False

    return "\n".join(program)

def run_file(input_file):
    if not os.path.exists(input_file):
        print(f"Fișierul {input_file} nu a fost găsit!")
        return

    print(f"Procesez {input_file}...")
    tests = parse_input_file(input_file)
    results = []
    total_lines = 0

    for t in tests:
        res = solve_case(t)
        results.append(res)
        total_lines += len(res.split('\n'))

    output_file = input_file.replace("in_", "out_")
    with open(output_file, 'w') as f:
        f.write("\n\n".join(results) + "\n")

    print(f"Salvat: {output_file} | Linii totale de instrucțiuni: {total_lines}")

def main():
    target_files = [
        'in_level-6_1-small.txt',
        'in_level-6_2-medium.txt',
        'in_level-6_3-large.txt',
        'in_level-6_4-enormous.txt'
    ]

    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        for f in target_files:
            if os.path.exists(f):
                run_file(f)

if __name__ == '__main__':
    main()
