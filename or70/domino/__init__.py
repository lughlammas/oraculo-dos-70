"""Domino Engine: conjunto duplo-n imutável, tiragem com SplitMix64 seedável ou manual."""
from dataclasses import dataclass

MASK = (1 << 64) - 1

class SplitMix64:
    def __init__(self, seed: int):
        self.s = seed & MASK
    def next(self) -> int:
        self.s = (self.s + 0x9E3779B97F4A7C15) & MASK
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
        return z ^ (z >> 31)
    def below(self, n: int) -> int:  # rejeição: sem viés de módulo
        lim = MASK - (MASK + 1) % n
        while True:
            x = self.next()
            if x <= lim:
                return x % n

@dataclass(frozen=True)
class Piece:
    position: int
    top: int
    bottom: int
    @property
    def id(self) -> str:
        a, b = sorted((self.top, self.bottom))
        return f"{a}-{b}"
    @property
    def sum(self) -> int:
        return self.top + self.bottom

def full_set(n: int = 6) -> tuple[tuple[int, int], ...]:
    return tuple((a, b) for a in range(n + 1) for b in range(a, n + 1))

@dataclass(frozen=True)
class Draw:
    pieces: tuple[Piece, ...]
    @property
    def U(self): return sum(p.top for p in self.pieces)
    @property
    def L(self): return sum(p.bottom for p in self.pieces)
    @property
    def T(self): return self.U + self.L

def validate(draw: Draw, n: int = 6) -> list[str]:
    """Auditoria operacional: duplicatas, faces fora do conjunto, limites [15,69] p/ 7 e T∈[1,70]."""
    errs, ids = [], [p.id for p in draw.pieces]
    if len(set(ids)) != len(ids): errs.append("peça duplicada")
    if any(not (0 <= v <= n) for p in draw.pieces for v in (p.top, p.bottom)): errs.append("face fora do conjunto")
    k = len(draw.pieces)
    if k == 7 and not 15 <= draw.T <= 69: errs.append(f"T={draw.T} fora de [15,69]")
    if k >= 8: errs.append("modalidade expandida (8+): exige regra de exceção")
    if not 1 <= draw.T <= 70: errs.append(f"T={draw.T} fora de [1,70]: exige regra de exceção")
    return errs

class Engine:
    def __init__(self, n: int = 6):
        self.n, self.set = n, full_set(n)
    def draw(self, seed: int, k: int = 7) -> Draw:
        rng, pool = SplitMix64(seed), list(self.set)
        out = []
        for i in range(k):  # Fisher-Yates parcial + orientação
            j = i + rng.below(len(pool) - i)
            pool[i], pool[j] = pool[j], pool[i]
            a, b = pool[i]
            if rng.below(2): a, b = b, a
            out.append(Piece(i + 1, a, b))
        return Draw(tuple(out))
    @staticmethod
    def manual(pairs) -> Draw:
        return Draw(tuple(Piece(i + 1, a, b) for i, (a, b) in enumerate(pairs)))
