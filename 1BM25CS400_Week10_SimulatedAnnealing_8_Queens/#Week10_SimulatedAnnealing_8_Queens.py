#Week10_SimulatedAnnealing_8_Queens
import random
import math

def calculate_attacks(state):
    """Calculates the number of attacking queen pairs (conflicts) in the state."""
    n = len(state)
    attacks = 0
    for i in range(n):
        for j in range(i + 1, n):
            if state[i] == state[j] or abs(state[i] - state[j]) == abs(i - j):
                attacks += 1
    return attacks

def get_random_neighbor(state):
    """Generates a neighbor by moving one queen in a random column to a different random row."""
    n = len(state)
    neighbor = list(state)
    col = random.randint(0, n - 1)
    current_row = state[col]
    new_row = random.randint(0, n - 1)
    while new_row == current_row:
        new_row = random.randint(0, n - 1)
    neighbor[col] = new_row
    return neighbor

def simulated_annealing_8queens(initial_temp=100.0, cooling_rate=0.995, min_temp=0.001):
    """Solves the 8-Queens problem using Simulated Annealing."""
    n = 8
    # Generate a random initial state
    current_state = [random.randint(0, n - 1) for _ in range(n)]
    current_cost = calculate_attacks(current_state)

    temp = initial_temp
    step = 0

    print(f"Initial State: {current_state} (Cost: {current_cost})")

    while temp > min_temp and current_cost > 0:
        step += 1
        neighbor = get_random_neighbor(current_state)
        neighbor_cost = calculate_attacks(neighbor)

        delta_e = neighbor_cost - current_cost

        # If the move is better, or accepted with a probability based on Temperature
        if delta_e < 0:
            current_state = neighbor
            current_cost = neighbor_cost
        else:
            acceptance_probability = math.exp(-delta_e / temp)
            if random.random() < acceptance_probability:
                current_state = neighbor
                current_cost = neighbor_cost

        # Cool down the system
        temp *= cooling_rate

        if step % 100 == 0:
            print(f"Iteration {step} | Temp: {temp:.4f} | Current Cost: {current_cost}")

    print(f"\nSearch Finished in {step} steps.")
    return current_state, current_cost

def print_board(state):
    """Displays the 8-Queens board visually."""
    n = len(state)
    for row in range(n):
        line = ""
        for col in range(n):
            if state[col] == row:
                line += " Q "
            else:
                line += " . "
        print(line)
    print(f"State Board representation: {state}")

# Run Simulated Annealing
final_state, final_cost = simulated_annealing_8queens()
print("\n--- Final Board Layout ---")
print_board(final_state)
print(f"Conflicts (Attacks): {final_cost}")
if final_cost == 0:
    print("SUCCESS: Found a valid 8-Queens solution!")
else:
    print("FAILURE: Failed to resolve all conflicts. Try running the simulation again.")