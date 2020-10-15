import random
import math

def generate_random_variable(l=12):
    u = random.uniform(0, 1)
    x = (-1 / l) * math.log(1 - u)
    return x

class Node:
    def __init__(self, arrival_times, collisions):
        self.arrival_times = arrival_times
        self.collisions = collisions

def generate_packet_arrivals(num_nodes, T_sim):
    nodes = []
    for i in range(num_nodes):
        curr_time = 0
        arrival_times = []

        while curr_time < T_sim:
            curr_time += generate_random_variable()
            if curr_time < T_sim:
                arrival_times.append(curr_time)

        arrival_times.reverse()
        nodes.append(Node(arrival_times, 0))

    return nodes

def find_min_queue(nodes):
    smallest_arrivals = []
    for node in nodes:
        if not len(node.arrival_times) > 0:
            continue
        smallest_arrivals.append(node.arrival_times[-1])

    if len(smallest_arrivals) == 0:
        return None

    smallest_arrival = min(smallest_arrivals)
    for i in range(len(nodes)):
        if not len(nodes[i].arrival_times) > 0:
            continue

        if nodes[i].arrival_times[-1] == smallest_arrival:
            return i

    return None

def persistent_csma_cd(nodes, T_sim, D, C, S, L, R):
    total_tx = 0
    successful_tx = 0

    curr_time = 0
    min_queue_idx = 0
    while curr_time < T_sim:
        # Determine queue with lowest arrival packet time stamp
        smallest_arrivals = []
        for node in nodes:
            if not len(node.arrival_times) > 0:
                continue
            smallest_arrivals.append(node.arrival_times[-1])

        if len(smallest_arrivals) == 0:
            break

        smallest_arrival = min(smallest_arrivals)
        for i in range(len(nodes)):
            if not len(nodes[i].arrival_times) > 0:
                continue

            if nodes[i].arrival_times[-1] == smallest_arrival:
                min_queue_idx = i
                break

        curr_time = smallest_arrival
        print(curr_time)

        collision_occurred = False

        # Determine if there are any collisions with packet arrivals in nodes from left to right
        for i in range(len(nodes)):
            if i == min_queue_idx:
                continue

            T_prop = (D / S) * abs(i - min_queue_idx)
            T_first_bit = nodes[min_queue_idx].arrival_times[-1] + T_prop
            T_final_bit = nodes[min_queue_idx].arrival_times[-1] + T_prop + (L / R)

            if not len(nodes[i].arrival_times) > 0:
                continue

            if nodes[i].arrival_times[-1] < T_first_bit:
                collision_occurred = True
                nodes[i].collisions += 1

                if nodes[i].collisions > 10:
                    nodes[i].arrival_times.pop()
                    nodes[i].collisions = 0
                    continue

                T_backoff = random.randint(0, (2**nodes[i].collisions) - 1) * (512 / R)
                T_wait = T_final_bit + T_backoff
                for j in reversed(range(len(nodes[i].arrival_times))):
                    if nodes[i].arrival_times[j] < T_wait:
                        nodes[i].arrival_times[j] = T_wait
                        total_tx += 1
                    else:
                        break

        if collision_occurred:
            collision_occurred = False
            T_backoff = random.randint(0, (2**nodes[min_queue_idx].collisions) - 1) * (512 / R)
            T_prop_furthest = (D / S) * abs(max(i - len(nodes), i - 0))
            T_furthest = nodes[min_queue_idx].arrival_times[-1] + T_prop_furthest + (L / R) + T_backoff

            nodes[min_queue_idx].collisions += 1
            if nodes[min_queue_idx].collisions <= 10:
                for i in reversed(range(len(nodes[min_queue_idx].arrival_times))):
                    if nodes[min_queue_idx].arrival_times[i] < T_furthest:
                        nodes[min_queue_idx].arrival_times[i] = T_furthest
                    else:
                        break
            else:
                nodes[min_queue_idx].arrival_times.pop()
                nodes[min_queue_idx].collisions = 0
        else:
            for i in range(len(nodes)):
                # Packet arrives at node during an ongoing transmission
                for j in reversed(range(len(nodes[i].arrival_times))):
                    if nodes[i].arrival_times[j] > T_first_bit and nodes[i].arrival_times[j] < T_final_bit:
                        nodes[i].arrival_times[j] = T_final_bit
            
            nodes[min_queue_idx].arrival_times.pop()
            nodes[min_queue_idx].collisions = 0
            successful_tx += 1
        
        total_tx += 1
    
    print("DONE!")
    print(successful_tx / total_tx)

C = 3 * (10 ** 8)
S = (2 / 3) * C
D = 10
L = 1500
R = 10**6
nodes = generate_packet_arrivals(20, 100)
persistent_csma_cd(nodes, 100, D, C, S, L, R)

                

        

