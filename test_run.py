from eegvibe import run_tracking, run_replay
from time import sleep
import numpy

if __name__ == '__main__':
    
    print("STARTING - PLEASE WAIT")
    
    condition = 3  
    sound_label = ''
    replay = 0
    
    
    if condition == 1:  # -90
        phase = -numpy.pi/2
    elif condition == 2:  # 180
        phase = numpy.pi 
    elif condition == 3: # +90
        phase = numpy.pi/2
    elif condition == 4:  # 0
        phase = 0
        
        
    if not replay:    
        run_tracking(freq_sample = 1000, freq_target = 10, phase_target = phase, freq_high_pass = 3, 
            oscilltrack_suppresion = 0.8, oscilltrack_gamma = 0.005,
            is_CL_stim = True, N_pulses = 40, pulse_duration = 0.02, ITI = 1, IPI = 0.08, stim_device_ID = 1,
            channel_track = 14, channels_ref =  [8, 9, 19, 20], channels_EMG = [32],  # channels_ref = range(0,31)
            N_plot_samples = 1000, plot_labels = ["Track", "EMG"], recording_duration = 30,
            participant_ID = 1, condition_label = sound_label, filename_data = './test_data/eeg_rest.csv'
            )
        
     
    if replay: 
        run_replay(freq_sample = 1000, freq_high_pass = 3,
            is_CL_stim = True, filename_stim = './out_data/06_03_2023_P1_Ch14_FRQ=50Hz_FULL_CL_phase=90.0_v1.pkl',
            channel_track = 14, channels_ref = [8, 9, 19, 20], channels_EMG = [32],
            N_plot_samples = 1000, plot_labels = ["Track", "EMG1"], recording_duration = 30,
            participant_ID = 1 #, filename_data = './test_data/eeg_rest.csv'
            )
