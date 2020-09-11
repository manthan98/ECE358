import random
import math
import time
from enum import Enum

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

    while len(events) > 0:
        event = events.pop(0)
        if event.time >= T:
            break

        print(event.time, event.event_type)

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
                departure_time = service_time + (last_departure_time if last_departure_time != 0 else event.time)
                if departure_time < T:
                    events.append(Event(departure_time, EventType.DEPARTURE))
                    events.sort(key=lambda x: x.time, reverse=False)
                num_arrivals += 1
            elif event.event_type == EventType.DEPARTURE:
                last_departure_time = event.time
                num_departures += 1
            else:
                total_packets += buffer_length
                observations += 1
    
    e_n = total_packets / observations
    idle = (empty_counter / observations) * 100
    print("Finished simulation: ", e_n, idle)
    return (e_n, idle)

def q3():
    E_N = []
    P_idle = []
    for i in range(0.25, 1.05, 0.1):
        rho, C, L, = i, 10 ** 6, 2000
        l = rho * (C / L)
        T = 50
        events = buildEventsForInfiniteBuffer(T, l)
        infiniteBufferDes(events, T, L, C)

rho, C, L = 0.85, 10 ** 6, 2000
l = rho * (C / L)
T = 50
events = buildEventsForInfiniteBuffer(T, l)
infiniteBufferDes(events, T, L, C)

# rho = 0.25 - Finished simulation:  0.20161675312688965 80.13271379014035
# rho = 0.35 - Finished simulation:  0.27125114995400185 73.65455381784729
# rho = 0.45 - Finished simulation:  0.3428809887416983 67.23905245587243
# rho - 0.55 - Finished simulation:  0.38393324417049485 63.922486480200035
# rho - 0.65 - Finished simulation:  0.45480400643007296 58.178558179794734
# rho - 0.75 - Finished simulation:  0.5186591439937714 53.897676006015296
# rho - 0.85 - Finished simulation:  0.5697346239084727 50.62508287083515