import random
import math

# -------------------------------
# Locations (lat, lon)
# Example: depot + food pickup sites
# -------------------------------
cities = [
    (40.7128, -74.0060),  # Depot (NYC)
    (40.730610, -73.935242),
    (40.650002, -73.949997),
    (40.8448, -73.8648),
    (40.6782, -73.9442),
    (40.7580, -73.9855),
    (40.7061, -74.0092)
]

POP_SIZE = 120
GENERATIONS = 500
MUTATION_RATE = 0.02
ELITE_SIZE = 10


# -------------------------------
# Haversine Distance
# -------------------------------

def haversine(coord1, coord2):
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    R = 6371  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


# -------------------------------
# Fitness
# -------------------------------

def total_distance(route):
    dist = 0
    for i in range(len(route)):
        dist += haversine(cities[route[i]], cities[route[(i+1) % len(route)]])
    return dist


# -------------------------------
# GA Functions
# -------------------------------

def create_route():
    route = list(range(len(cities)))
    random.shuffle(route)
    return route

def create_population():
    return [create_route() for _ in range(POP_SIZE)]

def rank_routes(population):
    return sorted(population, key=lambda r: total_distance(r))

def crossover(parent1, parent2):
    start, end = sorted(random.sample(range(len(parent1)), 2))
    child = [-1] * len(parent1)
    child[start:end] = parent1[start:end]

    p2_idx = 0
    for i in range(len(child)):
        if child[i] == -1:
            while parent2[p2_idx] in child:
                p2_idx += 1
            child[i] = parent2[p2_idx]

    return child

def mutate(route):
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(route)), 2)
        route[i], route[j] = route[j], route[i]
    return route


# -------------------------------
# Main Loop
# -------------------------------

def genetic_algorithm():
    population = create_population()

    for gen in range(GENERATIONS):
        ranked = rank_routes(population)
        next_gen = ranked[:ELITE_SIZE]

        while len(next_gen) < POP_SIZE:
            p1, p2 = random.sample(ranked[:50], 2)
            child = crossover(p1, p2)
            child = mutate(child)
            next_gen.append(child)

        population = next_gen

        if gen % 50 == 0:
            print(f"Generation {gen}, Best Distance: {total_distance(population[0]):.2f} km")

    best = rank_routes(population)[0]
    return best


# -------------------------------
# Run
# -------------------------------
def calculate_best_route():
    best_route = genetic_algorithm()

    #print("\nBest route (index order):", best_route)
    #print("Distance (km):", total_distance(best_route))

    #print("\nRoute coordinates:")
    
    return best_route
