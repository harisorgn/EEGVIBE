import numpy as np
from math import atan2

class Oscilltrack:
    a = 0.0
    b = 0.0
    re = 0.0
    im = 0.0
    theta = 0.0
    sinv = 0.0
    cosv = 1.0

    def __init__(self, freq_target, phase_target, freq_sample, suppression_cycle, gamma = None):
        self.phase_target = phase_target
        self.w = 2 * np.pi * freq_target / freq_sample
        self.gamma = 125/freq_sample if gamma is None else gamma
        self.suppression_reset = int(round(suppression_cycle * freq_sample / freq_target))
        self.suppression_count = 0
        self.is_prev_above_thrs = False

    def update(self, data):
        
        Delta = self.pred_error(data)
        self.a += self.gamma * Delta * self.sinv
        self.b += self.gamma * Delta * self.cosv

        self.theta += self.w
        # Wrap theta in the range [-pi, pi] for numerical stability
        if self.theta >= np.pi:
           self.theta -= 2*np.pi

        self.sinv = np.sin(self.theta)
        self.cosv = np.cos(self.theta)
        self.re = self.a * self.sinv + self.b * self.cosv
        self.im = self.b * self.sinv - self.a * self.cosv 

    def pred_error(self, data):
        # Calculates the error between the predicted signal value and the actual data at a timestep.
        # Used internally in the update function to update self.a and self.b .
        # This is a separate function for debug purposes.
        return data - self.re
    
    def get_phase(self):
        return atan2(self.im, self.re)

    def decide_stim(self):
        phase = self.get_phase()
        phase_rotated = phase - self.phase_target
        if phase_rotated >= np.pi:
            phase_rotated -= 2*np.pi
        elif phase_rotated < -np.pi:
            phase_rotated += 2*np.pi

        is_stim = False
        is_above_thrs = phase_rotated >= 0
        
        if is_above_thrs and (not self.is_prev_above_thrs) and (phase_rotated < np.pi/2):
            is_stim = self.suppression_count == 0
            self.suppression_count = self.suppression_reset

        self.is_prev_above_thrs = is_above_thrs
        if self.suppression_count > 0 :
            self.suppression_count -= 1
        else :
            self.suppression_count = 0
        
        return is_stim
