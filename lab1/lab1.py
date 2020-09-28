import random
import math
import time
from enum import Enum
import matplotlib.pyplot as plt

from multiprocessing import Pool, cpu_count

# Enumeration that defines the different event types.
class EventType(Enum):
    ARRIVAL = 0
    DEPARTURE = 1
    OBSERVER = 2

# Data structure that describes an event based on it's simulation time and type.
class Event:
    def __init__(self, time, event_type):
        self.time = time
        self.event_type = event_type

def generateRandomVariable(l=75):
    u = random.uniform(0, 1)
    x = (-1 / l) * math.log(1 - u)
    return x

def buildEventsForInfiniteBuffer(T, l, L, C):
    event_queue = []
    delta_t, obs_t = 0, 0

    last_departure_time = 0
    while delta_t < T or obs_t < T:
        if delta_t < T:
            # Determine the next arrival event time, create the arrival event, and
            # add it to the queue.
            delta_t += generateRandomVariable(l)
            arrival_event = Event(delta_t, EventType.ARRIVAL)
            event_queue.append(arrival_event)

            # Compute the service time as L / C, where L follows exp. dist.
            service_time = generateRandomVariable(1 / L) / C

            # If arrival time occurs before last departure event has exited queue,
            # then we compute departure event time as last time + service time. Otherwise,
            # compute as arrival time + service time (no other packets in queue).
            if arrival_event.time < last_departure_time:
                departure_event = Event(last_departure_time + service_time, EventType.DEPARTURE)
            else:
                departure_event = Event(arrival_event.time + service_time, EventType.DEPARTURE)
            last_departure_time = departure_event.time

            event_queue.append(departure_event)
        
        if obs_t < T:
            # Add observer events at a rate 5x that of arrival events.
            obs_t += generateRandomVariable(5 * l)
            observer_event = Event(obs_t, EventType.OBSERVER)
            event_queue.append(observer_event)
    
    event_queue.sort(key=lambda x: x.time, reverse=True)
    return event_queue

def infiniteBufferDes(events, T, L, C):
    # Setup variables for computing e_n and p_loss.
    num_arrivals, num_departures, total_packets, observations, empty_counter = 0, 0, 0, 0, 0

    while len(events) > 0:
        event = events.pop()
        if event.time >= T:
            break

        print(event.time, event.event_type)

        if event.event_type == EventType.ARRIVAL:
            num_arrivals += 1
        elif event.event_type == EventType.DEPARTURE:
            num_departures += 1
        else:
            # Determine the buffer length and increment total packets that have
            # been observed.
            buffer_length = num_arrivals - num_departures
            total_packets += buffer_length
            observations += 1
            if buffer_length == 0:
                empty_counter += 1
    
    # e_n is average # of packets based on total # of observer events.
    e_n = total_packets / observations

    # p_idle if average # of times empty buffer was observed based 
    # on total # of observer events.
    p_idle = (empty_counter / observations) * 100 
    return (e_n, p_idle)

def buildEventsForFiniteDes(T, l):
    event_queue = []
    delta_t, obs_t = 0, 0

    while delta_t < T or obs_t < T:
        if delta_t < T:
            delta_t += generateRandomVariable(l)
            event_queue.append(Event(delta_t, EventType.ARRIVAL))

        if obs_t < T:
            obs_t += generateRandomVariable(5 * l)
            event_queue.append(Event(obs_t, EventType.OBSERVER))
    
    event_queue.sort(key=lambda x: x.time, reverse=True)
    return event_queue

def testRobustnessOfFiniteBuffer():
    # rho_steps = [0.5, 1.5]
    rho = 1.5
    K_steps = 25
    T = 4000
    L, C = 2000, 10 ** 6
    l = rho * (C / L)
    event_queue = buildEventsForFiniteDes(T,l)
    e_n, p_loss, p_idle = finiteBufferDes(T, l, L, C, K_steps, event_queue)
    print("E[n]: ", e_n, " P_loss: ", p_loss, " p_idle: ", p_idle)    

def finiteBufferDes(T, l, L, C, K, events):
    num_arrivals, num_departures, total_packets, observations, empty_counter = 0, 0, 0, 0, 0
    last_departure_time, loss_counter = 0, 0
    lost_arrivals = 0

    departure_times = []
    while len(events) > 0:
        departure_time = departure_times[0] if len(departure_times) > 0 else float('inf')
        event = events[len(events)-1]

        if event.time >= T or last_departure_time >= T:
            break

        buffer_length = num_arrivals - num_departures
        if event.time < departure_time:
            events.pop()
            if event.event_type == EventType.ARRIVAL:
                print("ARRIVAL", event.time)
                if buffer_length == K:
                    loss_counter += 1
                    lost_arrivals += 1
                    continue

                service_time = generateRandomVariable(1 / L) / C
                if buffer_length == 0:
                    last_departure_time = service_time + event.time
                    departure_times.append(last_departure_time)
                else:
                    last_departure_time += service_time
                    departure_times.append(last_departure_time)
                
                num_arrivals += 1
            else:
                print("OBSERVER", event.time)
                total_packets += buffer_length
                observations += 1
                if buffer_length == 0:
                    empty_counter += 1
        else:
            print("DEPARTURE", departure_time)
            departure_times.pop(0)
            num_departures += 1
    
    e_n = total_packets / observations
    p_loss = (loss_counter / (num_arrivals + lost_arrivals)) * 100
    p_idle = (empty_counter / observations) * 100
    # print(e_n, p_loss, p_idle)
    return (e_n, p_loss, p_idle)

def q1():
    random_variables = []
    for i in range(0, 1000):
        random_variables.append(generateRandomVariable())

    mean = sum(random_variables) / len(random_variables)
    variance = sum((xi - mean) ** 2 for xi in random_variables) / len(random_variables)

    # E(x) for exponential random variable = 1 / lambda
    # Var(x) for exponential random variable = 1 / lambda^2
    # https://math.berkeley.edu/~scanlon/m16bs04/ln/16b2lec31.pdf
    print(mean, variance)

def infiniteBufferDesWrapper(args):
    return infiniteBufferDes(*args)

def buildEventsForInfiniteBufferWrapper(args):
    return buildEventsForInfiniteBuffer(*args)

def finiteBufferDesWrapper(args):
    return finiteBufferDes(*args)

def buildEventsForFiniteBufferWrapper(args):
    return buildEventsForFiniteDes(*args)

# Takes ~7 minutes for T = 1000
def q3(T=1000):
    # Setup lists to append values to as: 0.25 < rho < 0.95.
    E_N = []
    P_idle = []

    # Total # of CPU cores we can use to multiprocess the simulation.
    pool = Pool(cpu_count())

    C, L, = 10 ** 6, 2000
    rho_list = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    events_list_args = []

    # For each value of rho, we compute the arrival rate, and append to our
    # args list to be used for generating all events for all rho.
    for rho in rho_list:
        l = rho * (C / L)
        events_list_args.append((T, l, L, C))
    
    # List of arr/obs/dep events for each value of rho from 0.25 to 0.95.
    events_list = pool.map(buildEventsForInfiniteBufferWrapper, events_list_args)

    # For each list of events, append to our args list for the DES.
    des_args = []
    for events in events_list:
        des_args.append((events, T, L, C))
    
    # Multiprocess the DES, and strip out the e_n and p_idle values from each
    # simulation for each rho.
    results = pool.map(infiniteBufferDesWrapper, des_args)
    for result in results:
        E_N.append(result[0])
        P_idle.append(result[1])

    f = plt.figure()
    plt.plot(rho_list, E_N)
    plt.title(r'E[N] vs $\rho$')
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel('Average number in system E[N]')
    plt.show()
    f.savefig("en_q3_figure.pdf")

    f = plt.figure()
    plt.plot(rho_list, P_idle)
    plt.title(r'$P_{idle}$ vs $\rho$')
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel(r'$P_{idle}$ (%)')
    plt.show()
    f.savefig("pidle_q3_figure.pdf")

def q4():
    rho, C, L = 1.2, 10 ** 6, 2000
    l = rho * (C / L)
    T = 1000
    events = buildEventsForInfiniteBuffer(T, l, L, C)
    des = infiniteBufferDes(events, T, L, C)
    print(des[0], des[1])

def q6():
    # Setup lists to append values to as: 0.5 < rho < 1.5.
    E_Ns = []
    P_LOSSes = []

    # Total # of CPU cores we can use to multiprocess the simulation.
    pool = Pool(cpu_count())

    rho_steps = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    K_steps = [10, 25, 50]
    T = 1000
    L, C = 2000, 10 ** 6

    events_list_args = []
    des_list_args = []
    K_args = []
    l_args = []
    for K in K_steps:
        for rho in rho_steps:
            l = rho * (C / L)
            events_list_args.append((T,l))
            K_args.append(K)
            l_args.append(l)
    
    events_list = pool.map(buildEventsForFiniteBufferWrapper, events_list_args)
    print("done building events")
    
    # T, l, L, C, K, events
    for events, K, l in zip(events_list, K_args, l_args):
        des_list_args.append((T, l, L, C, K, events))

    results = pool.map(finiteBufferDesWrapper, des_list_args)
    print("done running simulation")

    count = 0
    e_n = []
    p_loss = []
    for result in results:
        e_n.append(result[0])
        p_loss.append(result[1])
        if count % (len(rho_steps) - 1) == 0 and count != 0:
            E_Ns.append(e_n)
            P_LOSSes.append(p_loss)
            e_n = []
            p_loss = []
            count = 0
        else:
            count = count + 1
        
    for i in range(len(E_Ns)):
        plt.plot(rho_steps, E_Ns[i], label=f"K = {K_steps[i]}")
    plt.legend(loc="upper left")
    plt.title(r'E[N] vs $\rho$ as K increases')
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel('Average number in system E[N]')
    plt.show()

    for i in range(len(P_LOSSes)):
        plt.plot(rho_steps, P_LOSSes[i], label=f"K = {K_steps[i]}")
    plt.legend(loc="upper left")
    plt.title(r'$P_{loss}$ vs $\rho$ as K increases')
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel(r'$P_{loss}$ (%)')
    plt.show()

# testRobustnessOfFiniteBuffer()
q6()