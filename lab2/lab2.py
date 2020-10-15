import random
import math
import collections

def generate_random_variable(l=12):
    u = random.uniform(0, 1)
    x = (-1 / l) * math.log(1 - u)
    return x

class Node:
    def __init__(self, arrival_times, collisions, latest_arrival_time):
        self.arrival_times = arrival_times
        self.collisions = collisions
        self.latest_arrival_time = latest_arrival_time

def generate_packet_arrivals(num_nodes, T_sim):
    nodes = []
    for i in range(num_nodes):
        curr_time = 0
        arrival_times = collections.deque([])

        while curr_time < T_sim:
            curr_time += generate_random_variable()
            if curr_time < T_sim:
                arrival_times.append(curr_time)

        nodes.append(Node(arrival_times, 0, arrival_times[0], float('-inf')))
    return nodes

def persistent_csma_cd(nodes, T_sim, D, C, S, L, R):
    total_tx = 0
    successful_tx = 0

    curr_time = 0
    min_queue_idx = 0
    while curr_time < T_sim:
        curr_time = float('inf')
        for i in range(len(nodes)):
            if nodes[i].latest_arrival_time < curr_time:
                curr_time = nodes[i].latest_arrival_time
                min_queue_idx = i

        if curr_time == float('inf'):
            break

        print(curr_time)

        collision_occurred = False

        # Determine if there are any collisions with packet arrivals in nodes from left to right
        for i in range(len(nodes)):
            if i == min_queue_idx:
                continue

            T_prop = (D / S) * abs(i - min_queue_idx)
            T_first_bit = nodes[min_queue_idx].arrival_times[0] + T_prop
            T_final_bit = nodes[min_queue_idx].arrival_times[0] + T_prop + (L / R)

            if not len(nodes[i].arrival_times) > 0:
                continue

            if nodes[i].arrival_times[0] < T_first_bit:
                collision_occurred = True
                nodes[i].collisions += 1

                if nodes[i].collisions > 10:
                    nodes[i].arrival_times.popleft()
                    nodes[i].collisions = 0
                    if len(nodes[i].arrival_times) > 0:
                        nodes[i].latest_arrival_time = nodes[i].arrival_times[0]
                    else:
                        nodes[i].latest_arrival_time = float('inf')
                    continue

                T_backoff = random.randint(0, (2**nodes[i].collisions) - 1) * (512 / R)
                T_wait = T_final_bit + T_backoff
                for j in range(len(nodes[i].arrival_times)):
                    if nodes[i].arrival_times[j] < T_wait:
                        nodes[i].arrival_times[j] = T_wait
                        nodes[i].latest_arrival_time = T_wait
                        total_tx += 1
                    else:
                        break

        if collision_occurred:
            collision_occurred = False
            T_backoff = random.randint(0, (2**nodes[min_queue_idx].collisions) - 1) * (512 / R)
            T_prop_furthest = (D / S) * abs(max(i - len(nodes), i - 0))
            T_furthest = nodes[min_queue_idx].arrival_times[0] + T_prop_furthest + (L / R) + T_backoff

            nodes[min_queue_idx].collisions += 1
            if nodes[min_queue_idx].collisions <= 10:
                for i in range(len(nodes[min_queue_idx].arrival_times)):
                    if nodes[min_queue_idx].arrival_times[i] < T_furthest:
                        nodes[min_queue_idx].arrival_times[i] = T_furthest
                        nodes[min_queue_idx].latest_arrival_time = T_furthest
                    else:
                        break
            else:
                nodes[min_queue_idx].arrival_times.popleft()
                nodes[min_queue_idx].collisions = 0
                if len(nodes[min_queue_idx].arrival_times) > 0:
                    nodes[min_queue_idx].latest_arrival_time = nodes[min_queue_idx].arrival_times[0]
                else:
                    nodes[min_queue_idx].latest_arrival_time = float('inf')
        else:
            for i in range(len(nodes)):
                # Packet arrives at node during an ongoing transmission
                for j in range(len(nodes[i].arrival_times)):
                    if nodes[i].arrival_times[j] > T_first_bit and nodes[i].arrival_times[j] < T_final_bit:
                        nodes[i].arrival_times[j] = T_final_bit
                if len(nodes[i].arrival_times) > 0:
                    nodes[i].latest_arrival_time = nodes[i].arrival_times[0]

            nodes[min_queue_idx].arrival_times.popleft()
            nodes[min_queue_idx].collisions = 0
            if len(nodes[min_queue_idx].arrival_times) > 0:
                nodes[min_queue_idx].latest_arrival_time = nodes[min_queue_idx].arrival_times[0]
            else:
                nodes[min_queue_idx].latest_arrival_time = float('inf')
            successful_tx += 1
        
        total_tx += 1
    
    print("DONE!")
    print(successful_tx / total_tx)

C = 3 * (10 ** 8)
S = (2 / 3) * C
D = 10
L = 1500
R = 10**6
nodes = generate_packet_arrivals(100, 100)
persistent_csma_cd(nodes, 100, D, C, S, L, R)

                

        

