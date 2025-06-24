import numpy as np
from hackrf_sweep import HackRFSweeper
from web_server import run_web_server, update_plot
from plot_spectrogram import SpectrogramBuffer
import threading
import time
from scipy import signal

def main():
    # Define frequency bands to sweep
    bands = [
        (2.1e9, 2.4e9),    # 2.1 GHz to 2.4 GHz
        (5.1e9, 5.4e9),    # 5.1 GHz to 5.4 GHz
        (5.6e9, 5.8e9),    # 5.6 GHz to 5.8 GHz
    ]
    
    # Configuration
    sample_rate = 20e6    # 20 MHz sample rate
    gain = 40            # RX gain in dB
    step_size = 5e6      # 5 MHz step size
    duration_per_step = 0.1  # 100ms per step
    
    # Create buffers for each frequency band
    buffers = [SpectrogramBuffer(sample_rate=sample_rate) for _ in bands]
    
    # Start web server in a separate thread
    server_thread = threading.Thread(
        target=run_web_server,
        kwargs={'host': '10.0.4.93', 'port': 5000}
    )
    server_thread.daemon = True
    server_thread.start()
    
    print("Web server started at http://10.0.4.93:5000")
    print("Using FAKE MODE - generating synthetic data instead of using HackRF hardware")
    print("Press Ctrl+C to stop...")
    
    try:
        with HackRFSweeper(sample_rate=sample_rate, gain=gain, fake_mode=True) as sweeper:
            while True:  # Continue until keyboard interrupt
                # Initialize lists to store results
                all_segments = []
                all_sample_rates = []
                all_center_freqs = []
                band_titles = []
                
                # Sweep each band
                for i, (start_freq, stop_freq) in enumerate(bands):
                    print(f"\nSweeping band {i+1}: {start_freq/1e9:.2f} GHz to {stop_freq/1e9:.2f} GHz")
                    
                    # Perform sweep
                    freqs, iq_data = sweeper.sweep_band(
                        start_freq=start_freq,
                        stop_freq=stop_freq,
                        step_size=step_size,
                        duration_per_step=duration_per_step
                    )
                    
                    # Store results
                    all_segments.extend(iq_data)
                    all_sample_rates.extend([sample_rate] * len(iq_data))
                    all_center_freqs.extend(freqs)
                    band_titles.extend([f"Band {i+1} - {f/1e9:.2f} GHz" for f in freqs])
                
                # Update the web plot
                update_plot(
                    segments=all_segments,
                    sample_rates=all_sample_rates,
                    center_freqs=all_center_freqs,
                    titles=band_titles,
                    buffers=buffers
                )
                
                # Small delay to prevent overwhelming the web server
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nStopping sweep...")
    finally:
        print("Shutting down...")

if __name__ == "__main__":
    main() 