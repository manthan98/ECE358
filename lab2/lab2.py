import os
import matplotlib as mpl
# if os.environ.get('DISPLAY','') == '':
#     print('no display found. Using non-interactive Agg backend')
#     mpl.use('Agg')
import matplotlib.pyplot as plt
import random
import math
import collections
import matplotlib.pyplot as plt

def generate_random_variable(l=5):
    u = random.uniform(0, 1)
    x = (-1 / l) * math.log(1 - u)
    return x

class Packet:
    def __init__(self, arrival_time, collisions, bus_busy_counter):
        self.arrival_time = arrival_time
        self.collisions = collisions
        self.bus_busy_counter = bus_busy_counter

class Node:
    def __init__(self, packets):
        self.packets = packets

# Creates nodes and populates them with a queue of packets, based on inputs.
# N: number of nodes.
# A: arrival rate of packets at each node.
# T_sim: desired simulation time.
# The output is a list of nodes.
def populate_nodes(N, A, T_sim):
    nodes = []

    # Create packet arrival times using Poisson distribution with packet arrival
    # rate defined by A. We create a deque, and as long as each arrival time is valid we
    # add to the deque. We then create a node with those packets at the end and repeat this
    # process for all nodes, defined by N.
    for i in range(N):
        curr_time = 0
        packets = collections.deque()

        while curr_time < T_sim:
            curr_time += generate_random_variable(A)
            if curr_time < T_sim:
                packets.append(Packet(curr_time, 0, 0))
        
        nodes.append(Node(packets))
    
    return nodes

# Simulates the persistent CSMA/CD network scenario.
# N: number of the nodes on the network.
# A: arrival rate of packets at each node.
# T_sim: desired simulation time.
# D: distance between each node.
# S: propagation speed of the medium.
# L: packet size.
# R: transmission rate over the link.
# The method outputs the efficiency and throughput of the network based on the inputs.
def persistent_csma_cd(N, A, T_sim, D, S, L, R):
    # Generate arrival packets at each node up to the simulation time.
    nodes = populate_nodes(N, A, T_sim)

    # Variables to keep track of successful and overall number of transmissions.
    success_tx, total_tx = 0, 0

    # Variables to keep track of simulation time and transmitting node index.
    curr_time, min_queue_idx = 0, 0
    
    while curr_time < T_sim:

        # Compute the node (and associated node index) that has smallest packet arrival time, by checking
        # if a node's latest packet arrival time is smaller than previous, smallest packet arrival time.
        curr_time = float('inf')
        for i in range(N):
            if not len(nodes[i].packets) > 0:
                continue
            if nodes[i].packets[0].arrival_time < curr_time and nodes[i].packets[0].arrival_time < T_sim:
                min_queue_idx = i
                curr_time = nodes[i].packets[0].arrival_time
        
        # This indicates that all nodes are empty - exit condition from simulation.
        if curr_time == float('inf'):
            break

        print(curr_time)

        # To keep track of any collisions between transmitting node and all other nodes.
        collision_detected = False

        # Scan all nodes (except transmitting node) to determine if there are any collisions.
        for idx, node in enumerate(nodes):
            if idx == min_queue_idx:
                continue
            if not len(node.packets) > 0:
                continue
            
            packet = node.packets[0]
            T_prop = (D / S) * abs(idx - min_queue_idx) # Propagation delay based on distance between transmitting and current node.

            # Determine if node's latest packet time is to be transmitted before first bit of transmitting
            # node is received - this indicates a collision between the transmitting and current loop node.
            if packet.arrival_time <= nodes[min_queue_idx].packets[0].arrival_time + T_prop:
                total_tx += 1
                collision_detected = True

                packet.collisions += 1
                
                # If the packet has been involved in more than 10 collisions, drop it and update the arrival time of the next packet in the node
                # if there is one. We only change the packet's arrival time if it is less than the dropped packet's arrival time.
                if packet.collisions > 10:
                    last_packet = node.packets.popleft()
                    if len(node.packets) > 0:
                        node.packets[0].arrival_time = max(node.packets[0].arrival_time, last_packet.arrival_time)
                else:
                    # Apply an exponential backoff to the node's packet time based on number of collisions - time node must wait before it can
                    # retransmit this packet.
                    T_backoff = random.randint(0, 2**packet.collisions - 1) * (512 / R)
                    packet.arrival_time += T_backoff
        
        # Helper variables to access transmitter node and packet.
        transmitter_node = nodes[min_queue_idx]
        transmitter_node_packet = transmitter_node.packets[0]
        
        # If the transmitting node collided with any other nodes, it's packet arrival time must be updated (or dropped). Otherwise, the packet
        # must be removed from the transmitting node's packet queue.
        if collision_detected:
            total_tx += 1

            transmitter_node_packet.collisions += 1
            if transmitter_node_packet.collisions > 10:
                last_packet = transmitter_node.packets.popleft()
                if len(transmitter_node.packets) > 0:
                    transmitter_node.packets[0].arrival_time = max(transmitter_node.packets[0].arrival_time, last_packet.arrival_time)
            else:
                T_backoff = random.randint(0, 2**transmitter_node_packet.collisions - 1) * (512 / R)
                transmitter_node_packet.arrival_time += T_backoff
        else:
            success_tx += 1
            total_tx += 1

            last_packet = transmitter_node.packets.popleft()
            if len(transmitter_node.packets) > 0:
                transmitter_node.packets[0].arrival_time = max(transmitter_node.packets[0].arrival_time, last_packet.arrival_time)
            
            # Scan every node on the bus and update the latest packet arrivals in the case that there were packets that were to be transmitted
            # during a busy bus (while the transmitting node was transmitting).
            for i in range(len(nodes)):
                if not len(nodes[i].packets) > 0:
                    continue

                packet = nodes[i].packets[0]
                T_prop = abs(i - min_queue_idx) * (D / S)

                # If this node's packet was to be transmitted after the first bit, but before the last bit of the current transmitting node's packet,
                # we must re-schedule the packet to after the last bit of the current transmitting node's packet passes this node  on the bus.
                if transmitter_node_packet.arrival_time + T_prop <= packet.arrival_time < transmitter_node_packet.arrival_time + T_prop + L / R:
                    packet.arrival_time = transmitter_node_packet.arrival_time + T_prop + L / R
                    
    print("Done simulation!")
    efficiency = success_tx / total_tx
    throughput = ((success_tx * L) / T_sim) / (10**6)
    print(efficiency, throughput)
    return (efficiency, throughput)

# Simulates the persistent CSMA/CD network scenario.
# N: number of the nodes on the network.
# A: arrival rate of packets at each node.
# T_sim: desired simulation time.
# D: distance between each node.
# S: propagation speed of the medium.
# L: packet size.
# R: transmission rate over the link.
# The method outputs the efficiency and throughput of the network based on the inputs.
def non_persistent_csma_cd(N, A, T_sim, D, S, L, R):
    # Generate arrival packets at each node up to the simulation time.
    nodes = populate_nodes(N, A, T_sim)

    # Variables to keep track of successful and overall number of transmissions.
    success_tx, total_tx = 0, 0

    # Variables to keep track of simulation time and transmitting node index.
    curr_time, min_queue_idx = 0, 0
    
    while curr_time < T_sim:

        # Compute the node (and associated node index) that has smallest packet arrival time, by checking
        # if a node's latest packet arrival time is smaller than previous, smallest packet arrival time.
        curr_time = float('inf')
        for i in range(N):
            if not len(nodes[i].packets) > 0:
                continue
            if nodes[i].packets[0].arrival_time < curr_time and nodes[i].packets[0].arrival_time < T_sim:
                min_queue_idx = i
                curr_time = nodes[i].packets[0].arrival_time
        
        # This indicates that all nodes are empty - exit condition from simulation.
        if curr_time == float('inf'):
            break

        # print(curr_time)

        # To keep track of any collisions between transmitting node and all other nodes.
        collision_detected = False

        # Scan all nodes (except transmitting node) to determine if there are any collisions.
        for idx, node in enumerate(nodes):
            if idx == min_queue_idx:
                continue
            if not len(node.packets) > 0:
                continue
            
            packet = node.packets[0]
            T_prop = (D / S) * abs(idx - min_queue_idx) # Propagation delay based on distance between transmitting and current node.

            # Determine if node's latest packet time is to be transmitted before first bit of transmitting
            # node is received - this indicates a collision between the transmitting and current loop node.
            if packet.arrival_time <= nodes[min_queue_idx].packets[0].arrival_time + T_prop:
                total_tx += 1
                collision_detected = True

                packet.collisions += 1
                
                # If the packet has been involved in more than 10 collisions, drop it and update the arrival time of the next packet in the node
                # if there is one. We only change the packet's arrival time if it is less than the dropped packet's arrival time.
                if packet.collisions > 10:
                    last_packet = node.packets.popleft()
                    if len(node.packets) > 0:
                        node.packets[0].arrival_time = max(node.packets[0].arrival_time, last_packet.arrival_time)
                else:
                    # Apply an exponential backoff to the node's packet time based on number of collisions - time node must wait before it can
                    # retransmit this packet.
                    T_backoff = random.randint(0, 2**packet.collisions - 1) * (512 / R)
                    packet.arrival_time += T_backoff
        
        # Helper variables to access transmitter node and packet.
        transmitter_node = nodes[min_queue_idx]
        transmitter_node_packet = transmitter_node.packets[0]
        
        # If the transmitting node collided with any other nodes, it's packet arrival time must be updated (or dropped). Otherwise, the packet
        # must be removed from the transmitting node's packet queue.
        if collision_detected:
            total_tx += 1

            transmitter_node_packet.collisions += 1
            if transmitter_node_packet.collisions > 10:
                last_packet = transmitter_node.packets.popleft()
                if len(transmitter_node.packets) > 0:
                    transmitter_node.packets[0].arrival_time = max(transmitter_node.packets[0].arrival_time, last_packet.arrival_time)
            else:
                T_backoff = random.randint(0, 2**transmitter_node_packet.collisions - 1) * (512 / R)
                transmitter_node_packet.arrival_time += T_backoff
        else:
            success_tx += 1
            total_tx += 1

            # Node was able to successfully transmit the packet, so we reset the busy counter on the packet.
            transmitter_node_packet.bus_busy_counter = 0

            last_packet = transmitter_node.packets.popleft()
            if len(transmitter_node.packets) > 0:
                transmitter_node.packets[0].arrival_time = max(transmitter_node.packets[0].arrival_time, last_packet.arrival_time)
            
            # Scan every node on the bus and update the latest packet arrivals in the case that there were packets that were to be transmitted
            # during a busy bus (while the transmitting node was transmitting).
            for i in range(len(nodes)):
                if not len(nodes[i].packets) > 0:
                    continue

                packet = nodes[i].packets[0]
                T_prop = abs(i - min_queue_idx) * (D / S)

                # If this node's packet was to be transmitted after the first bit, but before the last bit of the current transmitting node's packet,
                # we must re-schedule the packet to be its current time plus an exponential backoff
                while transmitter_node_packet.arrival_time + T_prop <= packet.arrival_time < transmitter_node_packet.arrival_time + T_prop + L / R:
                    if packet.bus_busy_counter < 10:
                        packet.bus_busy_counter += 1
                    else:
                        last_packet = nodes[i].packets.popleft()
                        if len(nodes[i].packets) > 0:
                            nodes[i].packets[0].arrival_time = max(nodes[i].packets[0].arrival_time, last_packet.arrival_time)
                        break

                    T_random_wait = random.randint(0, 2**packet.bus_busy_counter - 1) * (512 / R)
                    packet.arrival_time += T_random_wait
                    
    print("Done simulation!")
    efficiency = success_tx / total_tx
    throughput = ((success_tx * L) / T_sim) / (10**6)
    print(efficiency, throughput)
    return (efficiency, throughput)

def test():
    A = [7]
    N = [100]
    T_sim = 1000
    S = 2 * (10**8)
    D = 10
    L = 1500
    R = 10**6

    overall_res = []
    for a in A:
        res = []
        for n in N:
            eff = non_persistent_csma_cd(n, a, T_sim, D, S, L, R)
            res.append(eff)
        overall_res.append(res)
    
    for res in overall_res:
        plt.plot(N, res)
    # plt.show()

def q1():
    A = [7, 10, 20]
    N = [20, 30, 40, 50, 60, 70, 80, 90, 100]
    T_sim = 1000
    C = 3 * (10**8)
    S = (2 / 3) * C
    D = 10
    L = 1500
    R = 10**6

    overall_efficiencies = []
    overall_throughputs = []
    for a in A:
        efficiencies = []
        throughputs = []
        for n in N:
            res = persistent_csma_cd(n, a, T_sim, D, S, L, R)
            efficiencies.append(res[0])
            throughputs.append(res[1])
        overall_efficiencies.append(efficiencies)
        overall_throughputs.append(throughputs)
    
    f = plt.figure()
    for idx, efficiencies in enumerate(overall_efficiencies):
        plt.plot(N, efficiencies, label=f"A = {A[idx]}")
    plt.title("Efficiency vs Number of nodes for persistent CSMA/CD")
    plt.xlabel("Number of nodes (N)")
    plt.ylabel("Efficiency")
    plt.legend(loc="upper right")
    plt.show()
    f.savefig("persistent_csma_cd_eff")

    f = plt.figure()
    for idx, throughputs in enumerate(overall_throughputs):
        plt.plot(N, throughputs, label=f"A = {A[idx]}")
    plt.title("Throughput vs Number of nodes for persistent CSMA/CD")
    plt.xlabel("Number of node (N)")
    plt.ylabel("Throughput (Mbps)")
    plt.legend(loc="lower right")
    plt.show()
    f.savefig("persistent_csma_cd_tput")

def q2():
    A = [7, 10, 20]
    N = [20, 40, 60, 80, 100]
    T_sim = 100 # reduced for the sake of faster testing
    C = 3 * (10**8)
    S = (2 / 3) * C
    D = 10
    L = 1500
    R = 10**6

    overall_efficiencies = []
    overall_throughputs = []
    for a in A:
        efficiencies = []
        throughputs = []
        for n in N:
            res = non_persistent_csma_cd(n, a, T_sim, D, S, L, R)
            efficiencies.append(res[0])
            throughputs.append(res[1])
        overall_efficiencies.append(efficiencies)
        overall_throughputs.append(throughputs)
    
    f = plt.figure()
    for idx, efficiencies in enumerate(overall_efficiencies):
        plt.plot(N, efficiencies, label=f"A = {A[idx]}")
    plt.title("Efficiency vs Number of nodes for Non-Persistent CSMA/CD")
    plt.xlabel("Number of nodes (N)")
    plt.ylabel("Efficiency")
    plt.legend(loc="upper right")
    plt.show()
    f.savefig("non_persistent_csma_cd_eff")

    f = plt.figure()
    for idx, throughputs in enumerate(overall_throughputs):
        plt.plot(N, throughputs, label=f"A = {A[idx]}")
    plt.title("Throughput vs Number of nodes for Non-Persistent CSMA/CD")
    plt.xlabel("Number of node (N)")
    plt.ylabel("Throughput (Mbps)")
    plt.legend(loc="lower right")
    plt.show()
    f.savefig("non_persistent_csma_cd_tput")

# Call method here
q2()
