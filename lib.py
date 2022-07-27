from math import exp
import numpy as np

# cubic feet to cubic meters
def f3_to_m3(f3):
    return f3 * 0.0283168

# Time to clear 99% of particles
def clearance_time_99(ach):
    if ach == 0:
        return "∞"
    return int((np.log(100) / ach) * 60)

# Time to clear 99.9% of particles
def clearance_time_999(ach):
    if ach == 0:
        return "∞"
    return int((np.log(1000) / ach) * 60)

co2_cubic_meter_per_hour = 0.05
co2_outdoor = 0.000420

def co2_by_time(t, co2_rate, people, ach, volume, co2_init):
    q = co2_rate
    n = ach if ach > 0 else 0.1
    V = volume

    result = (q*people / (n * V)) * (1 - (1 / exp(n * t)))
    result += ((co2_init - co2_outdoor) * (1 / exp(n*t)))
    result += co2_outdoor
    
    # Retun in ppm
    return result * 1000000