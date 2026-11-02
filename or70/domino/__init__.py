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

GEN_PROFILE = {"prng": "splitmix64", "prng_version": "1 (Steele/Vigna 2014, consts padrão)",
    "initial_order": "lexicográfica (a,b) com a<=b, a=0..n",
    "sampling": "Fisher-Yates parcial, inteiros por rejeição (sem viés de módulo)",
    "orientation_rule": "após cada peça, rng.below(2)==1 troca topo/base"}

def recompute(draw: Draw) -> dict:
    return {"upper_line_sum": draw.U, "lower_line_sum": draw.L, "total_sum": draw.T}

def modality(k: int) -> str:
    return "padrao-7" if k == 7 else ("expandida-declarada" if k >= 8 else f"reduzida-{k}")

def validate(draw: Draw, n: int = 6, declared_count: int | None = None) -> dict:
    """Erros invalidam a tiragem; avisos não. Identidade canônica não orientada (3/4 == 4/3)."""
    errs, warns, ps = [], [], draw.pieces
    if [p.position for p in ps] != list(range(1, len(ps) + 1)): errs.append("posições não sequenciais")
    if any(not (isinstance(v, int) and 0 <= v <= n) for p in ps for v in (p.top, p.bottom)): errs.append(f"face fora de 0..{n}")
    if declared_count is not None and declared_count != len(ps): errs.append(f"pieces_count declarado {declared_count} != {len(ps)}")
    ids = [p.id for p in ps]
    if len(set(ids)) != len(ids): errs.append("peça física duplicada")
    if len(ps) == 7 and not errs and not 15 <= draw.T <= 69: errs.append(f"T={draw.T} fisicamente impossível p/ 7 peças distintas")
    if len(ps) >= 8: warns.append("modalidade expandida declarada (8+ peças)")
    return {"valid": not errs, "errors": errs, "warnings": warns, "modality": modality(len(ps))}

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
