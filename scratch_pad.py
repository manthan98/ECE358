import random
import math
import collections

def generate_random_variable(l=12):
    u = random.uniform(0, 1)
    x = (-1 / l) * math.log(1 - u)
    return x

def generate_packet_arrivals(num_nodes, T_sim):
    arrival_packets = []
    for i in range(num_nodes):
        curr_time = 0
        curr_packets = []

        while curr_time < T_sim:
            curr_time += generate_random_variable()
            if curr_time < T_sim:
                curr_packets.append(curr_time)
        
        curr_packets.reverse()
        arrival_packets.append(curr_packets)

    print(len(arrival_packets))
    return arrival_packets

def persistent_csma_cd(num_nodes, arrival_packets, T_sim, D, S, L, R):
    total_tx, success_tx = 0, 0

    min_queue_idx = 0
    curr_time = 0

    collisions = [0] * num_nodes

    while curr_time < T_sim:
        curr_time = float('inf')
        for i in range(len(arrival_packets)):
            if not len(arrival_packets[i]) > 0:
                continue
            if arrival_packets[i][-1] < curr_time:
                curr_time = arrival_packets[i][-1]
                min_queue_idx = i
        
        if curr_time == float('inf'):
            break

        print(curr_time)
        collision_detected = False

        for i in range(len(arrival_packets)):
            if i == min_queue_idx:
                continue
            if not len(arrival_packets[i]) > 0:
                continue

            T_prop = (D / S) * abs(i - min_queue_idx)
            T_first_bit = arrival_packets[min_queue_idx][-1] + T_prop
            T_final_bit = arrival_packets[min_queue_idx][-1] + T_prop + (L / R)

            if arrival_packets[i][-1] < T_first_bit:
                collision_detected = True
                collisions[i] += 1

                if collisions[i] > 10:
                    collisions[i] = 10
                    arrival_packets[i].pop()
                else:
                    T_backoff = random.randrange(0, 2**collisions[i]) * (512 / R)
                    T_wait = T_final_bit + T_backoff
                    
                    for j in reversed(range(len(arrival_packets[i]))):
                        if arrival_packets[i][j] < T_wait:
                            arrival_packets[i][j] = T_wait
                            total_tx += 1
                
                total_tx += 1
        
        if collision_detected:
            collision_detected = False
            collisions[min_queue_idx] += 1

            if collisions[min_queue_idx] > 10:
                collisions[min_queue_idx] = 0
                arrival_packets[min_queue_idx].pop()
            else:
                # T_prop = (D / S) * max(len(arrival_packets) - min_queue_idx - 1, min_queue_idx - 0)
                T_backoff = random.randrange(0, 2**collisions[min_queue_idx]) * (512 / R)
                T_wait = arrival_packets[min_queue_idx][-1] + min(T_prop, (L / R)) + T_backoff

                for i in reversed(range(len(arrival_packets[min_queue_idx]))):
                    if arrival_packets[min_queue_idx][i] < T_wait:
                        arrival_packets[min_queue_idx][i] = T_wait
        else:
            for i in range(len(arrival_packets)):
                if i == min_queue_idx:
                    continue

                T_prop = (D / S) * abs(min_queue_idx - i)
                T_first_bit = arrival_packets[min_queue_idx][-1] + T_prop
                T_final_bit = arrival_packets[min_queue_idx][-1] + T_prop + (L / R)
                for j in reversed(range(len(arrival_packets[i]))):
                    if arrival_packets[i][j] > T_first_bit and arrival_packets[i][j] < T_final_bit:
                        arrival_packets[i][j] = T_final_bit
            
            collisions[min_queue_idx] = 0
            arrival_packets[min_queue_idx].pop()
            success_tx += 1
        
        total_tx += 1
    
    print("DONE!")
    print(success_tx / total_tx)


C = 3 * (10 ** 8)
S = (2 / 3) * C
D = 10
L = 1500
R = 10**6
arrival_packets = generate_packet_arrivals(20, 100)
persistent_csma_cd(20, arrival_packets, 200, D, S, L, R)