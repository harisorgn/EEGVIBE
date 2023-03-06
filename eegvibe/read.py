import zmq
from time import sleep
from .connect import generate_publisher, send_array, SerializingContext
#import eego_sdk
import numpy as np
import pandas as pd
import time
from warnings import warn

def get_freq_sample(freq_sample, amplifier_ID):
    factory = eego_sdk.factory()
    amplifiers = factory.getAmplifiers()
    amplifier = amplifiers[amplifier_ID]

    try:
        rates = amplifier.getSamplingRatesAvailable()
        rates.index(freq_sample)
        return freq_sample
    except:
        diff = [abs(freq_sample - r) for r in rates]
        idx = diff.index(min(diff))
        new_freq = rates[idx]
        warn(f"Sampling rate {freq_sample} is not available. Using rate={new_freq} as the closest available value.")
        return new_freq

def run_EEG_stream(freq_sample, event, socket, topic):
    factory = eego_sdk.factory()
    amplifiers = factory.getAmplifiers()
    amplifier = amplifiers[0]
    
    ref_ranges = amplifier.getReferenceRangesAvailable()
    bip_ranges = amplifier.getBipolarRangesAvailable()
    stream = amplifier.OpenEegStream(freq_sample, ref_ranges[1], bip_ranges[0])
    
    i = 0
    while not event.is_set():
        data = np.array(stream.getData())
        socket.send_string(topic, zmq.SNDMORE)
        #socket.send_pyobj(data)
        socket.send_array(data)
        i += 1
    sleep(0.005)  # Sleeps 5 milliseconds to be polite with the CPU
    print(f'Sent {i} samples')
    socket.send_string(topic, zmq.SNDMORE)
    #socket.send_pyobj('stop')
    socket.send_array(np.empty(0))

    sleep(1)  # Gives enough time to the subscribers to update their status

def get_impedance(amplifier_ID):
    factory = eego_sdk.factory()
    amplifiers = factory.getAmplifiers()
    amplifier = amplifiers[amplifier_ID]
    stream = amplifier.OpenImpedanceStream()
    return list(stream.getData())
    
def get_channel_names(amplifier_ID):
    factory = eego_sdk.factory()
    amplifiers = factory.getAmplifiers()
    amplifier = amplifiers[amplifier_ID]
    stream = amplifier.OpenImpedanceStream()
    channels = stream.getChannelList()
    return [str(c) for c in channels]

def stream_to_publish(freq_sample, event, port, topic = 'stream'):
    context = zmq.Context()
    socket = generate_publisher(port, context)

    run_EEG_stream(freq_sample, event, socket, topic)

    sleep(1)  # Gives enough time to the subscribers to update their status
    socket.close()

class DataIterator:
    def __init__(self, n_samples, freq_sample, data_file):
        self.n_samples = n_samples
        self.freq_sample = freq_sample
        self.counter = 0
        self.stop = False

        D = np.array(pd.read_csv(data_file))
        #self.data = D[:, :]
        self.data = D

        self.n_rows = len(self.data)

    def __iter__(self):
        return self

    def __next__(self):
        idx_start = self.n_samples * self.counter
        idx_end = idx_start + self.n_samples
        if idx_end <= self.n_rows:
            time.sleep(self.n_samples/self.freq_sample)   
            self.counter += 1

            if ((self.n_samples + 1) * self.counter) > self.n_rows:
                self.reset()

            next_data = np.ascontiguousarray(self.data[idx_start:idx_end,:])
            return next_data
        else:
            self.counter = 0 # reset iterator
            raise StopIteration

    def acquire_data(self, queue):
        while not self.stop:
            queue.put({'topic': 'sample', 'data': next(self)})

    def publish_data(self, port, topic = 'stream', topic_impedance = 'impedance'):
        #context = zmq.Context()
        context = SerializingContext()
        socket = generate_publisher(port, context)

        i = 0
        while not self.stop:
            data = next(self)
            socket.send_string(topic, zmq.SNDMORE)
            #socket.send_pyobj(data)
            socket.send_array(data)
            i += 1
        sleep(0.005)  # Sleeps 5 milliseconds to be polite with the CPU
        print(f'Sent {i} samples')
        socket.send_string(topic, zmq.SNDMORE)
        #socket.send_pyobj('stop')
        socket.send_array(np.empty(0))
        sleep(1)  # Gives enough time to the subscribers to update their status
        socket.close()

    def reset(self):
        self.counter = 0
    