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
    print(e_n, p_loss)
    return e_n

def q3():
    E_N = []
    P_idle = []

    rho_list = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85, 0.95]
    for rho in rho_list:
        C, L, = 10 ** 6, 2000
        l = rho * (C / L)
        T = 100
        events = buildEventsForInfiniteBuffer(T, l, L, C)
        E_N.append(infiniteBufferDes(events, T, L, C))
    plt.plot(E_N)
    plt.show()

q3()