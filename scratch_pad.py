import random
import math
import time
from enum import Enum
import matplotlib.pyplot as plt

class EventType(Enum):
    ARRIVAL = 0
    OBSERVER = 1

class Event:
    def __init__(self, time, event_type):
        self.time = time
        self.event_type = event_type

def generateRandomVariable(l=75):
    u = random.uniform(0, 1)
    x = (-1 / l) * math.log(1 - u)
    return x

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

def finiteBufferDesV2(T, l, L, C, K, events):
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

def finiteBufferDes(T, l, L, C, K, arrival_times, observer_times):
    num_arrivals, num_departures, total_packets, observations, empty_counter = 0, 0, 0, 0, 0
    last_departure_time, loss_counter = 0, 0

    departure_times = []
    while len(arrival_times) > 0:
        departure_time = departure_times[0] if len(departure_times) > 0 else float('inf')
        if arrival_times[0] >= T:
            break

        buffer_length = num_arrivals - num_departures
        if arrival_times[0] < departure_time and arrival_times[0] < observer_times[0]:
            arrival_time = arrival_times.pop(0)
            print("ARRIVAL", arrival_time)
            if buffer_length == K:
                loss_counter += 1
                continue

            num_arrivals += 1
            service_time = generateRandomVariable(1 / L) / C
            if buffer_length == 0:
                departure_times.append(arrival_time + service_time)
            else:
                departure_times.append(last_departure_time + service_time)
        elif observer_times[0] < arrival_times[0] and observer_times[0] < departure_time:
            observer_time = observer_times.pop(0)
            print("OBSERVER", observer_time)
            total_packets += buffer_length
            observations += 1
            if buffer_length == 0:
                empty_counter += 1
        elif departure_time < arrival_times[0] and departure_time < observer_times[0]:
            last_departure_time = departure_times.pop(0)
            print("DEPARTURE", last_departure_time)
            num_departures += 1
    
    e_n = total_packets / observations
    print(e_n, loss_counter)
    return (e_n, loss_counter)


# rho, L, C = 0.5, 2000, 10 ** 6
# T = 50
# l = rho * (C / L)
# K = 10
# events = buildEventsForFiniteDes(T, l)
# finiteBufferDesV2(T, l, L, C, K, events)

def q6():
    rho_steps = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]
    K_steps = [10, 25, 40]
    T = 50
    L, C = 2000, 10 ** 6

    E_Ns = []
    P_LOSSes = []

    for K in K_steps:
        e_n = []
        p_loss = []
        for rho in rho_steps:
            l = rho * (C / L)
            events = buildEventsForFiniteDes(T, l)
            des = finiteBufferDesV2(T, l, L, C, K, events)
            e_n.append(des[0])
            p_loss.append(des[1])
        E_Ns.append(e_n)
        P_LOSSes.append(p_loss)

    for i in range(len(E_Ns)):
        plt.plot(rho_steps, E_Ns[i], label=f"K = {K_steps[i]}")
    plt.legend(loc="upper left")
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel('Average number in system E[N]')
    plt.show()

    for i in range(len(P_LOSSes)):
        plt.plot(rho_steps, P_LOSSes[i], label=f"K = {K_steps[i]}")
    plt.legend(loc="upper left")
    plt.xlabel(r'Traffic Intensity ($\rho$)')
    plt.ylabel(r'$P_{loss}$ (%)')
    plt.show()

q6()