import random
import math
import time
from enum import Enum
import matplotlib.pyplot as plt

def generateRandomVariable(l=75):
    u = random.uniform(0, 1)
    x = (-1 / l) * math.log(1 - u)
    return x

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

class EventType(Enum):
    ARRIVAL = 0
    DEPARTURE = 1
    OBSERVER = 2

class Event:
    def __init__(self, time, event_type):
        self.time = time
        self.event_type = event_type

def buildEventsForInfiniteBuffer(T, l, L, C):
    event_queue = []
    delta_t, obs_t = 0, 0

    last_departure_time = 0
    while delta_t < T or obs_t < T:
        if delta_t < T:
            delta_t += generateRandomVariable(l)
            arrival_event = Event(delta_t, EventType.ARRIVAL)
            event_queue.append(arrival_event)

            service_time = generateRandomVariable(1 / L) / C
            if arrival_event.time < last_departure_time:
                departure_event = Event(last_departure_time + service_time, EventType.DEPARTURE)
            else:
                departure_event = Event(arrival_event.time + service_time, EventType.DEPARTURE)
            last_departure_time = departure_event.time

            event_queue.append(departure_event)
        
        if obs_t < T:
            obs_t += generateRandomVariable(5 * l)
            observer_event = Event(obs_t, EventType.OBSERVER)
            event_queue.append(observer_event)
    
    event_queue.sort(key=lambda x: x.time, reverse=False)
    return event_queue

def infiniteBufferDes(events, T, L, C):
    num_arrivals, num_departures, total_packets, observations, empty_counter = 0, 0, 0, 0, 0

    while len(events) > 0:
        event = events.pop(0)
        if event.time >= T:
            break

        print(event.time, event.event_type)

        if event.event_type == EventType.ARRIVAL:
            num_arrivals += 1
        elif event.event_type == EventType.DEPARTURE:
            num_departures += 1
        else:
            buffer_length = num_arrivals - num_departures
            total_packets += buffer_length
            observations += 1
            if buffer_length == 0:
                empty_counter += 1
    
    e_n = total_packets / observations
    p_loss = (empty_counter / observations) * 100
    return (e_n, p_loss)

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
    
    event_queue.sort(key=lambda x: x.time, reverse=False)
    return event_queue

def finiteBufferDes(T, l, L, C, K, events):
    num_arrivals, num_departures, total_packets, observations, empty_counter = 0, 0, 0, 0, 0
    last_departure_time, loss_counter = 0, 0
    lost_arrivals = 0

    departure_times = []
    while len(events) > 0:
        departure_time = departure_times[0] if len(departure_times) > 0 else float('inf')
        event = events[0]

        if event.time >= T or last_departure_time >= T:
            break

        buffer_length = num_arrivals - num_departures
        if event.time < departure_time:
            events.pop(0)
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
    print(e_n, p_loss, p_idle)
    return (e_n, p_loss, p_idle)

def q3():
    E_N = []
    P_idle = []

    rho_list = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    for rho in rho_list:
        C, L, = 10 ** 6, 2000
        l = rho * (C / L)
        T = 1000
        events = buildEventsForInfiniteBuffer(T, l, L, C)
        des = infiniteBufferDes(events, T, L, C)
        E_N.append(des[0])
        P_idle.append(des[1])

    plt.plot(rho_list, E_N)
    plt.title(r'E[N] vs $\rho$')
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel('Average number in system E[N]')
    plt.show()

    plt.plot(rho_list, P_idle)
    plt.title(r'$P_{idle}$ vs $\rho$')
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel(r'$P_{idle}$ (%)')
    plt.show()

def q4():
    rho, C, L = 1.2, 10 ** 6, 2000
    l = rho * (C / L)
    T = 50
    events = buildEventsForInfiniteBuffer(T, l, L, C)
    des = infiniteBufferDes(events, T, L, C)
    print(des[0], des[1])

def q6():
    rho_steps = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    K_steps = [10, 25, 40]
    T = 1000
    L, C = 2000, 10 ** 6

    E_Ns = []
    P_LOSSes = []

    for K in K_steps:
        e_n = []
        p_loss = []
        for rho in rho_steps:
            l = rho * (C / L)
            events = buildEventsForFiniteDes(T, l)
            des = finiteBufferDes(T, l, L, C, K, events)
            e_n.append(des[0])
            p_loss.append(des[1])
        E_Ns.append(e_n)
        P_LOSSes.append(p_loss)

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

# 0.33384482700686596 74.91899572297417 - rho = 0.25
# 0.5450760453016397 64.76329721919208 - rho = 0.35
# 0.8214175136658695 54.93777402915385 - rho = 0.45
# 1.2285164239287871 44.90221339097903 - rho = 0.55
# 1.853504090501381 34.938465487914414 - rho = 0.65
# 2.990750445418032 25.12546874183667 - rho = 0.75
# 5.829317597101947 14.61906566518453 - rho = 0.85
# 19.017634391211487 4.988878738447555 - rho = 0.95

# E_N = [0.33384482700686596, 0.5450760453016397, 0.8214175136658695, 1.2285164239287871, 1.853504090501381, 2.990750445418032, 5.829317597101947, 19.017634391211487]
# P_idle = [74.91899572297417, 64.76329721919208, 54.93777402915385, 44.90221339097903, 34.938465487914414, 25.12546874183667, 14.61906566518453, 4.988878738447555]
# rho_list = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]

# plt.plot(rho_list, E_N)
# plt.title(r'E[N] vs $\rho$')
# plt.xlabel(r'Traffic Intensity ($\rho$)')
# plt.ylabel('Average number in system E[N]')
# plt.show()

# plt.plot(rho_list, P_idle)
# plt.title(r'$P_{idle}$ vs $\rho$')
# plt.xlabel(r'Traffic Intensity ($\rho$)')
# plt.ylabel(r'$P_{idle}$ (%)')
# plt.show()

# 49884.367167411154 0.00043322762579264 - rho = 1.2
