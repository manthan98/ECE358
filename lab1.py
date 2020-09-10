import random
import math
import time
from enum import Enum

def generateRandomVariable(l=75):
    u = random.uniform(0, 1)
    x = -1 * (1 / l) * math.log(1 - u)
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


def buildEventsForInfiniteBuffer(T, l):
    events = []
    delta_t, obs_t = 0, 0

    while delta_t < T or obs_t < T:
        if delta_t < T:
            delta_t += generateRandomVariable(l)
            events.append(Event(delta_t, EventType.ARRIVAL))

        if obs_t < T:
            obs_t += generateRandomVariable(5 * l)
            events.append(Event(obs_t, EventType.OBSERVER))
    
    events.sort(key=lambda x: x.time, reverse=False)
    return events

def infiniteBufferDes(events, T, L, C):
    num_arrivals, num_departures, total_packets, empty_counter = 0, 0, 0, 0
    last_departure_time = 0
    observations = 0
    e_n = 0

    print(len(events))
    while len(events) > 0:
        event = events.pop(0)
        if event.time >= T:
            break
        
        if event.event_type == EventType.OBSERVER:
            print(event.time)

        buffer_length = num_arrivals - num_departures
        if buffer_length == 0 and event.event_type == EventType.ARRIVAL:
            service_time = generateRandomVariable(1 / L) / C
            departure_time = service_time + event.time
            if departure_time < T:
                events.append(Event(departure_time, EventType.DEPARTURE))
                events.sort(key=lambda x: x.time, reverse=False)
            num_arrivals += 1
        elif buffer_length == 0 and event.event_type == EventType.OBSERVER:
            empty_counter += 1
            observations += 1
        else:
            if event.event_type == EventType.ARRIVAL:
                service_time = generateRandomVariable(1 / L) / C
                departure_time = service_time + last_departure_time
                if departure_time < T:
                    events.append(Event(departure_time, EventType.DEPARTURE))
                    events.sort(key=lambda x: x.time, reverse=False)
                num_arrivals += 1
            elif event.event_type == EventType.DEPARTURE:
                num_departures += 1
            else:
                total_packets += buffer_length
                observations += 1
                e_n += (e_n + buffer_length) / observations
    
    print("Finished simulation: ", e_n)

rho, C, L = 0.25, 10 ** 6, 2000
l = rho * (C / L)
T = 10
events = buildEventsForInfiniteBuffer(T, l)
infiniteBufferDes(events, T, L, C)