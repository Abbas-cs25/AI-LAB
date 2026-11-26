#fol resolution
import re
from itertools import combinations

# Literal representation for FOL
class Literal:
    def __init__(self, predicate, args, negated=False):
        self.predicate = predicate
        self.args = list(args)
        self.negated = negated

    def __str__(self):
        sign = "~" if self.negated else ""
        return f"{sign}{self.predicate}({','.join(self.args)})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            isinstance(other, Literal)
            and self.predicate == other.predicate
            and self.args == other.args
            and self.negated == other.negated
        )

    def __hash__(self):
        return hash((self.predicate, tuple(self.args), self.negated))

    def negate(self):
        return Literal(self.predicate, self.args, not self.negated)


def is_variable(term):
    # Variables start with a lowercase letter
    return term[0].islower()


def unify(lit1, lit2):
    if lit1.predicate != lit2.predicate:
        return None
    if len(lit1.args) != len(lit2.args):
        return None

    subst = {}

    def unify_terms(t1, t2):
        t1 = subst.get(t1, t1)
        t2 = subst.get(t2, t2)
        if t1 == t2:
            return True
        if is_variable(t1):
            subst[t1] = t2
            return True
        if is_variable(t2):
            subst[t2] = t1
            return True
        return False

    for a1, a2 in zip(lit1.args, lit2.args):
        if not unify_terms(a1, a2):
            return None
    return subst


def apply_subst(term, subst):
    if isinstance(term, Literal):
        new_args = [subst.get(arg, arg) for arg in term.args]
        return Literal(term.predicate, new_args, term.negated)
    return term


class Clause:
    def __init__(self, literals):
        self.literals = frozenset(literals)

    def __str__(self):
        if not self.literals:
            return "[] (Empty Clause)"
        return " ∨ ".join(str(lit) for lit in self.literals)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Clause) and self.literals == other.literals

    def __hash__(self):
        return hash(self.literals)

    def is_empty(self):
        return len(self.literals) == 0


def resolve(clause1, clause2):
    new_clauses = []
    for lit1 in clause1.literals:
        for lit2 in clause2.literals:
            if lit1.predicate == lit2.predicate and lit1.negated != lit2.negated:
                subst = unify(lit1, lit2.negate())
                if subst is not None:
                    resolved_lits = set()
                    for l in clause1.literals:
                        if l != lit1:
                            resolved_lits.add(apply_subst(l, subst))
                    for l in clause2.literals:
                        if l != lit2:
                            resolved_lits.add(apply_subst(l, subst))
                    new_clauses.append((Clause(resolved_lits), lit1, lit2))
    return new_clauses


def extract_clean_proof_steps(empty_clause, parent_map):
    # Reconstruct the minimal direct path of resolution steps leading to []
    steps = []
    def traverse(clause):
        if clause in parent_map:
            p1, p2, lit1, lit2 = parent_map[clause]
            traverse(p1)
            traverse(p2)
            steps.append((p1, p2, lit1, lit2, clause))
    traverse(empty_clause)

    # De-duplicate the tree steps to keep it linear and minimal
    seen = set()
    unique_steps = []
    for p1, p2, l1, l2, res in steps:
        if (p1, p2, res) not in seen:
            unique_steps.append((p1, p2, l1, l2, res))
            seen.add((p1, p2, res))
    return unique_steps


def prove_by_resolution(kb_clauses, query_literal):
    print("\n--- STEP 1 & 2: Converting Premises & Negated Query to CNF ---")
    clauses = set(kb_clauses)
    negated_query = Clause([query_literal.negate()])
    clauses.add(negated_query)

    print("\n--- STEP 3: Initial Clause Set (with Negated Query) ---")
    for i, c in enumerate(sorted(list(clauses), key=lambda x: str(x)), 1):
        print(f"Clause {i}: {c}")
    print("="*70)

    # Map to store {resolvent: (parent_a, parent_b, resolved_lit_a, resolved_lit_b)}
    parent_map = {}

    print("\n--- STEP 4: Starting Resolution Loop (Searching minimal proof path) ---")
    while True:
        pairs = list(combinations(clauses, 2))
        new_generated = set()
        found_new = False

        for c1, c2 in pairs:
            resolvents = resolve(c1, c2)
            for resolvent, lit1, lit2 in resolvents:
                if resolvent not in clauses and resolvent not in new_generated:
                    parent_map[resolvent] = (c1, c2, lit1, lit2)

                    if resolvent.is_empty():
                        # Extract only the 5-6 direct active proof steps
                        proof_steps = extract_clean_proof_steps(resolvent, parent_map)

                        print(f"\n🎯 Contradiction Derived in {len(proof_steps)} Direct Steps!")
                        print("=================== DIRECT TEXTBOOK PROOF PATH ===================")
                        for idx, (p1, p2, l1, l2, res) in enumerate(proof_steps, 1):
                            print(f"Step {idx}:")
                            print(f"   Parent A: {p1}")
                            print(f"   Parent B: {p2}")
                            print(f"   Resolved: {l1} with {l2}")
                            print(f"   👉 Resulting Clause: {res}\n")
                        print("==================================================================")
                        print("Result: 'John likes peanuts' is logically PROVED (TRUE)!")
                        print("="*70)
                        return True

                    new_generated.add(resolvent)
                    found_new = True

        if not found_new:
            print("\nNo contradiction could be found.")
            return False

        clauses.update(new_generated)


# --- Knowledge Base Definition ---
kb_premises = [
    # 1. Apple and vegetables are food
    Clause([Literal("Food", ["Apple"])]),
    Clause([Literal("Food", ["Vegetables"])]),

    # 2. John likes all kind of food: Food(x) => Likes(John, x)
    # CNF: ~Food(x) ∨ Likes(John, x)
    Clause([
        Literal("Food", ["x"], negated=True),
        Literal("Likes", ["John", "x"])
    ]),

    # 3. Anything anyone eats and not killed is food: Eats(x, y) & ~Killed(x) => Food(y)
    # CNF: ~Eats(x, y) ∨ Killed(x) ∨ Food(y)
    Clause([
        Literal("Eats", ["x", "y"], negated=True),
        Literal("Killed", ["x"]),
        Literal("Food", ["y"])
    ]),

    # 4. Anil eats peanuts
    Clause([Literal("Eats", ["Anil", "Peanuts"])]),

    # 5. Anil is alive (still alive)
    Clause([Literal("Alive", ["Anil"])]),

    # 6. Harry eats everything that Anil eats: Eats(Anil, z) => Eats(Harry, z)
    # CNF: ~Eats(Anil, z) ∨ Eats(Harry, z)
    Clause([
        Literal("Eats", ["Anil", "z"], negated=True),
        Literal("Eats", ["Harry", "z"])
    ]),

    # 7. Anyone who is alive implies not killed: Alive(x) => ~Killed(x)
    # CNF: ~Alive(x) ∨ ~Killed(x)
    Clause([
        Literal("Alive", ["x"], negated=True),
        Literal("Killed", ["x"], negated=True)
    ]),

    # 8. Anyone who is not killed implies alive: ~Killed(x) => Alive(x)
    # CNF: Killed(x) ∨ Alive(x)
    Clause([
        Literal("Killed", ["x"]),
        Literal("Alive", ["x"])
    ])
]

# Query: John likes peanuts
query_goal = Literal("Likes", ["John", "Peanuts"])

# Run FOL resolution proof
prove_by_resolution(kb_premises, query_goal)