import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from collections import deque

class SpectrogramBuffer:
    def __init__(self, max_time=5, sample_rate=20e6):
        self.max_time = max_time
        self.sample_rate = sample_rate
        self.buffer = deque(maxlen=int(max_time * sample_rate))
        self.time_points = deque(maxlen=int(max_time * sample_rate))
        self.current_time = 0
        
    def add_data(self, iq_data):
        self.buffer.extend(iq_data)
        new_time_points = np.linspace(self.current_time, 
                                    self.current_time + len(iq_data)/self.sample_rate,
                                    len(iq_data))
        self.time_points.extend(new_time_points)
        self.current_time = new_time_points[-1]
        
    def get_spectrogram(self, nperseg=1024, noverlap=512):
        if len(self.buffer) < nperseg:
            return None, None, None
            
        # Convert buffer to numpy array
        data = np.array(self.buffer)
        times = np.array(self.time_points)
        
        # Calculate spectrogram
        f, t, Sxx = signal.spectrogram(data, fs=self.sample_rate,
                                     nperseg=nperseg, noverlap=noverlap,
                                     return_onesided=False)
        
        # Adjust time points to match buffer times
        t = times[nperseg//2::nperseg-noverlap][:len(t)]
        
        return f, t, Sxx

def plot_spectrogram(iq_data, sample_rate, center_freq, title="Spectrogram", buffer=None):
    """
    Plot spectrogram from IQ data
    
    Args:
        iq_data (numpy.ndarray): Complex IQ samples
        sample_rate (float): Sample rate in Hz
        center_freq (float): Center frequency in Hz
        title (str): Plot title
        buffer (SpectrogramBuffer): Optional buffer for time accumulation
    """
    if buffer is None:
        buffer = SpectrogramBuffer(sample_rate=sample_rate)
    
    buffer.add_data(iq_data)
    f, t, Sxx = buffer.get_spectrogram()
    
    if f is None:
        return None
    
    # Shift frequencies to center frequency
    f = f + center_freq
    
    # Plot
    plt.figure(figsize=(12, 6))
    plt.pcolormesh(f/1e9, t, 10*np.log10(Sxx), shading='auto')
    plt.xlabel('Frequency [GHz]')
    plt.ylabel('Time [sec]')
    plt.title(title)
    plt.colorbar(label='Power [dB]')
    plt.tight_layout()
    
    return plt.gcf()

def plot_combined_spectrogram(segments, sample_rates, center_freqs, titles=None, buffers=None):
    """
    Plot multiple spectrograms from different frequency segments
    
    Args:
        segments (list): List of IQ data arrays
        sample_rates (list): List of sample rates
        center_freqs (list): List of center frequencies
        titles (list): Optional list of titles for each segment
        buffers (list): Optional list of SpectrogramBuffer objects
    """
    if titles is None:
        titles = [f"Segment {i+1}" for i in range(len(segments))]
    
    if buffers is None:
        buffers = [SpectrogramBuffer(sample_rate=sr) for sr in sample_rates]
    
    fig, axes = plt.subplots(len(segments), 1, figsize=(12, 4*len(segments)))
    if len(segments) == 1:
        axes = [axes]
    
    for i, (iq_data, fs, fc, title, buffer) in enumerate(zip(segments, sample_rates, center_freqs, titles, buffers)):
        buffer.add_data(iq_data)
        f, t, Sxx = buffer.get_spectrogram()
        
        if f is None:
            continue
            
        f = f + fc
        
        # Sort frequencies to fix pcolormesh warning
        sort_idx = np.argsort(f)
        f = f[sort_idx]
        Sxx = Sxx[sort_idx, :]
        
        im = axes[i].pcolormesh(f/1e9, t, 10*np.log10(Sxx), shading='auto')
        axes[i].set_xlabel('Frequency [GHz]')
        axes[i].set_ylabel('Time [sec]')
        axes[i].set_title(title)
        plt.colorbar(im, ax=axes[i], label='Power [dB]')
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    # Test parameters
    sample_rate = 20e6  # 20 MHz
    duration = 0.1      # 100ms
    center_freqs = [2.4e9, 5.2e9, 5.7e9]  # Test frequencies
    
    # Create buffers for each frequency
    buffers = [SpectrogramBuffer(sample_rate=sample_rate) for _ in center_freqs]
    
    # Generate test IQ data (complex sine waves with noise)
    t = np.linspace(0, duration, int(sample_rate * duration))
    segments = []
    
    for fc in center_freqs:
        # Create a complex signal with some noise
        signal_freq = 1e6  # 1 MHz tone
        iq_data = np.exp(1j * 2 * np.pi * signal_freq * t)
        iq_data += 0.1 * (np.random.randn(len(t)) + 1j * np.random.randn(len(t)))
        segments.append(iq_data)
    
    # Test single spectrogram
    print("Testing single spectrogram plot...")
    fig = plot_spectrogram(segments[0], sample_rate, center_freqs[0], "Test Single Spectrogram", buffers[0])
    if fig:
        plt.show()
    
    # Test combined spectrogram
    print("Testing combined spectrogram plot...")
    fig = plot_combined_spectrogram(
        segments=segments,
        sample_rates=[sample_rate] * len(segments),
        center_freqs=center_freqs,
        titles=[f"Test {i+1} - {fc/1e9:.1f} GHz" for i, fc in enumerate(center_freqs)],
        buffers=buffers
    )
    if fig:
        plt.show() 