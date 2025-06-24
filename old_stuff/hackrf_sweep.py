import numpy as np
from pyhackrf2 import HackRF
import time

class HackRFSweeper:
    def __init__(self, sample_rate=20e6, gain=40, fake_mode=False):
        """
        Initialize HackRF sweeper
        
        Args:
            sample_rate (float): Sample rate in Hz
            gain (int): RX gain in dB
            fake_mode (bool): If True, generate fake data instead of using HackRF
        """
        self.sample_rate = sample_rate
        self.gain = gain
        self.fake_mode = fake_mode
        self.device = None
        
    def __enter__(self):
        if not self.fake_mode:
            self.device = HackRF()
            self.device.sample_rate = self.sample_rate
            self.device.rx_gain = self.gain
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.device:
            self.device.close()
            
    def generate_fake_iq_data(self, center_freq, duration):
        """
        Generate fake IQ data for testing
        
        Args:
            center_freq (float): Center frequency in Hz
            duration (float): Capture duration in seconds
            
        Returns:
            numpy.ndarray: Complex IQ samples
        """
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples)
        
        # Create a complex signal with some noise and frequency-dependent characteristics
        # Add a tone at a frequency relative to the center frequency
        tone_freq = 1e6  # 1 MHz tone
        iq_data = np.exp(1j * 2 * np.pi * tone_freq * t)
        
        # Add some frequency-dependent amplitude variation
        freq_factor = (center_freq / 1e9) % 3  # Varies with frequency
        amplitude = 0.5 + 0.3 * np.sin(freq_factor * np.pi)
        iq_data *= amplitude
        
        # Add noise
        noise_level = 0.1
        iq_data += noise_level * (np.random.randn(num_samples) + 1j * np.random.randn(num_samples))
        
        # Add some frequency-dependent phase variation
        phase_variation = 0.1 * np.sin(2 * np.pi * 0.5 * t) * (center_freq / 1e9)
        iq_data *= np.exp(1j * phase_variation)
        
        return iq_data
            
    def capture_segment(self, center_freq, duration):
        """
        Capture IQ data for a specific frequency segment
        
        Args:
            center_freq (float): Center frequency in Hz
            duration (float): Capture duration in seconds
            
        Returns:
            numpy.ndarray: Complex IQ samples
        """
        if self.fake_mode:
            return self.generate_fake_iq_data(center_freq, duration)
            
        if not self.device:
            raise RuntimeError("Device not initialized. Use with context manager.")
            
        self.device.center_freq = center_freq
        num_samples = int(duration * self.sample_rate)
        
        # Start RX
        self.device.start_rx()
        
        # Collect samples
        samples = []
        while len(samples) < num_samples:
            data = self.device.rx()
            samples.extend(data)
            
        # Stop RX
        self.device.stop_rx()
        
        # Convert to numpy array and trim to requested length
        samples = np.array(samples[:num_samples])
        return samples
        
    def sweep_band(self, start_freq, stop_freq, step_size, duration_per_step):
        """
        Sweep a frequency band and capture data
        
        Args:
            start_freq (float): Start frequency in Hz
            stop_freq (float): Stop frequency in Hz
            step_size (float): Frequency step size in Hz
            duration_per_step (float): Capture duration per step in seconds
            
        Returns:
            tuple: (frequencies, iq_data)
        """
        frequencies = np.arange(start_freq, stop_freq, step_size)
        iq_data = []
        
        for freq in frequencies:
            print(f"Capturing at {freq/1e9:.2f} GHz...")
            samples = self.capture_segment(freq, duration_per_step)
            iq_data.append(samples)
            
        return frequencies, iq_data

if __name__ == "__main__":
    # Test parameters
    sample_rate = 20e6    # 20 MHz
    gain = 40            # 40 dB
    test_freq = 2.4e9    # 2.4 GHz
    duration = 0.1       # 100ms
    
    try:
        # Test single frequency capture
        print("Testing single frequency capture...")
        with HackRFSweeper(sample_rate=sample_rate, gain=gain) as sweeper:
            print(f"Capturing at {test_freq/1e9:.2f} GHz...")
            samples = sweeper.capture_segment(test_freq, duration)
            print(f"Captured {len(samples)} samples")
            print(f"Sample shape: {samples.shape}")
            print(f"Sample type: {samples.dtype}")
            print(f"Sample range: {np.min(samples)} to {np.max(samples)}")
        
        # Test band sweep
        print("\nTesting band sweep...")
        start_freq = 2.1e9  # 2.1 GHz
        stop_freq = 2.4e9   # 2.4 GHz
        step_size = 10e6    # 10 MHz
        duration_per_step = 0.1  # 100ms
        
        with HackRFSweeper(sample_rate=sample_rate, gain=gain) as sweeper:
            print(f"Sweeping from {start_freq/1e9:.2f} GHz to {stop_freq/1e9:.2f} GHz...")
            freqs, iq_data = sweeper.sweep_band(
                start_freq=start_freq,
                stop_freq=stop_freq,
                step_size=step_size,
                duration_per_step=duration_per_step
            )
            
            print(f"Completed sweep of {len(freqs)} frequencies")
            print(f"Number of IQ data segments: {len(iq_data)}")
            print(f"Shape of first segment: {iq_data[0].shape}")
            
    except Exception as e:
        print(f"Error during test: {str(e)}") 