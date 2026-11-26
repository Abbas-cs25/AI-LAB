class Node:
    def __init__(self, name, value=None, children=None):
        self.name = name
        self.value = value
        self.children = children if children is not None else []

# Alpha-Beta Pruning Implementation
def alpha_beta(node, depth, alpha, beta, is_max, pruned_info):
    # Terminal node / Leaf node
    if not node.children or depth == 0:
        print(f"Leaf Node {node.name}: Value = {node.value} (alpha={alpha}, beta={beta})")
        return node.value

    if is_max:
        max_val = float('-inf')
        for child in node.children:
            val = alpha_beta(child, depth - 1, alpha, beta, False, pruned_info)
            max_val = max(max_val, val)
            alpha = max(alpha, val)
            print(f"Node {node.name} (MAX): Evaluated child {child.name}. Value = {max_val}, alpha = {alpha}, beta = {beta}")
            if beta <= alpha:
                # Prune remaining children of this MAX node
                pruning_index = node.children.index(child) + 1
                if pruning_index < len(node.children):
                    pruned = [c.name for c in node.children[pruning_index:]]
                    pruned_info.append((node.name, pruned, f"alpha ({alpha}) >= beta ({beta})"))
                break
        node.value = max_val
        return max_val
    else:
        min_val = float('inf')
        for child in node.children:
            val = alpha_beta(child, depth - 1, alpha, beta, True, pruned_info)
            min_val = min(min_val, val)
            beta = min(beta, val)
            print(f"Node {node.name} (MIN): Evaluated child {child.name}. Value = {min_val}, alpha = {alpha}, beta = {beta}")
            if beta <= alpha:
                # Prune remaining children of this MIN node
                pruning_index = node.children.index(child) + 1
                if pruning_index < len(node.children):
                    pruned = [c.name for c in node.children[pruning_index:]]
                    pruned_info.append((node.name, pruned, f"beta ({beta}) <= alpha ({alpha})"))
                break
        node.value = min_val
        return min_val

# Constructing a classic test game tree of depth 3
# Level 3: Leaf nodes
l1 = Node("L1", value=10)
l2 = Node("L2", value=9)
l3 = Node("L3", value=14)
l4 = Node("L4", value=18)
l5 = Node("L5", value=5)
l6 = Node("L6", value=4)
l7 = Node("L7", value=50)
l8 = Node("L8", value=-3)

# Level 2: MIN nodes
b1 = Node("B1", children=[l1, l2])
b2 = Node("B2", children=[l3, l4])
c1 = Node("C1", children=[l5, l6])
c2 = Node("C2", children=[l7, l8])

# Level 1: MAX nodes under Root
a1 = Node("A1", children=[b1, b2])
a2 = Node("A2", children=[c1, c2])

# Level 0: Root MAX node
root = Node("Root", children=[a1, a2])

# Run alpha-beta pruning
pruned_branches = []
print("=== Alpha-Beta Pruning Execution Trace ===")
final_val = alpha_beta(root, depth=3, alpha=float('-inf'), beta=float('inf'), is_max=True, pruned_info=pruned_branches)

print("\n=== Results Summary ===")
print(f"Final value of MAX Node (Root): {final_val}")
print("\nSubtrees Pruned:")
if pruned_branches:
    for parent, nodes, reason in pruned_branches:
        print(f" - At Node '{parent}': Pruned children {nodes} because of rule: {reason}")
else:
    print(" - No subtrees were pruned.")