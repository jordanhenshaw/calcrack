import math

def find_mach_angle(Algorithm):
    return math.degrees(math.asin(Algorithm.speed_sound_mps / Algorithm.bullet_speed_mps))