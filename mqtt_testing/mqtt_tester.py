#!/usr/bin/env python3
"""
MQTT Tester - A comprehensive tool to send fake data to test the UI
This script can send various types of data including radar, antenna, messages, etc.
"""

import json
import time
import random
import base64
import argparse
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
from mqtt_debuger import MqttDebugger, MessageLevel


class MqttTester:
    """
    A comprehensive MQTT tester that can send various types of fake data
    to test the UI functionality.
    """
    
    def __init__(self, broker="127.0.0.1", port=1884, verbose=True):
        self.debugger = MqttDebugger(broker=broker, port=port, verbose=verbose)
        self.running = False
        
    def generate_fake_radar_data(self, num_targets=3):
        """Generate fake radar data with random targets"""
        ids = [f"TARGET_{i:02d}" for i in range(1, num_targets + 1)]
        azm = [random.uniform(0, 360) for _ in range(num_targets)]
        elv = [random.uniform(0, 90) for _ in range(num_targets)]
        colors = [f"#{random.randint(0, 255):02x}{random.randint(0, 255):02x}{random.randint(0, 255):02x}" 
                 for _ in range(num_targets)]
        
        return ids, azm, elv, colors
    
    def generate_fake_simulate_data(self, num_targets=2):
        """Generate fake simulation data"""
        ids = [f"-SIM_{i:02d}" for i in range(1, num_targets + 1)]  # Negative prefix for simulated data
        azm = [random.uniform(0, 360) for _ in range(num_targets)]
        elv = [random.uniform(0, 90) for _ in range(num_targets)]
        
        return ids, azm, elv
    
    def generate_fake_antenna_data(self):
        """Generate fake antenna data with 16 antennas"""
        powers = []
        received = []
        selected = []
        
        for i in range(16):
            # Randomly set some antennas to have data
            if random.random() > 0.3:  # 70% chance of having power data
                powers.append(random.uniform(-30, 10))
            else:
                powers.append(None)
                
            if random.random() > 0.4:  # 60% chance of having received data
                received.append(random.uniform(0, 10))
            else:
                received.append(None)
        
        # Select 2-4 random antennas
        num_selected = random.randint(2, 4)
        selected = random.sample(range(16), num_selected)
        
        return powers, received, selected
    
    def generate_fake_spectrogram(self):
        """Generate a fake spectrogram image"""
        # Create a fake spectrogram
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Generate fake frequency and time data
        freqs = np.linspace(0, 100, 100)
        times = np.linspace(0, 10, 50)
        
        # Create fake spectrogram data
        data = np.random.randn(100, 50) * 0.1
        # Add some fake signals
        for i in range(3):
            freq_idx = random.randint(10, 90)
            time_idx = random.randint(5, 45)
            data[freq_idx-5:freq_idx+5, time_idx-3:time_idx+3] += 2
        
        im = ax.imshow(data, aspect='auto', origin='lower', 
                      extent=[times[0], times[-1], freqs[0], freqs[-1]])
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Frequency (MHz)')
        ax.set_title('Fake Spectrogram')
        plt.colorbar(im, ax=ax)
        
        # Save to bytes
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def generate_fake_target_figure(self):
        """Generate a fake target figure"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Generate fake target data
        x = np.random.uniform(0, 100, 20)
        y = np.random.uniform(0, 50, 20)
        sizes = np.random.uniform(10, 100, 20)
        colors = np.random.rand(20)
        
        scatter = ax.scatter(x, y, s=sizes, c=colors, alpha=0.6)
        ax.set_xlabel('Range (m)')
        ax.set_ylabel('Azimuth (deg)')
        ax.set_title('Fake Target Detection')
        plt.colorbar(scatter, ax=ax)
        
        # Save to bytes
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return base64.b64encode(buf.read()).decode('utf-8')
    
    def send_all_data_types(self):
        """Send all types of data at once"""
        print("Sending all data types...")
        
        # Send radar data
        ids, azm, elv, colors = self.generate_fake_radar_data(3)
        self.debugger.send_radar(ids, azm, elv, colors)
        
        # Send simulate data
        sim_ids, sim_azm, sim_elv = self.generate_fake_simulate_data(2)
        self.debugger.send_simulate(sim_ids, sim_azm, sim_elv)
        
        # Send antenna data
        powers, received, selected = self.generate_fake_antenna_data()
        self.debugger.send_antenna(powers, received, selected)
        
        # Send spectrogram
        spec_fig = self.generate_fake_spectrogram()
        self.debugger.send_spectrogram(spec_fig)
        
        # Send target figure
        target_fig = self.generate_fake_target_figure()
        self.debugger.send_pf(target_fig)
        
        # Send some messages
        self.debugger.info("System initialized successfully")
        self.debugger.debug("Processing radar data...")
        self.debugger.warning("Low signal strength detected")
        
        print("All data types sent!")
    
    def run_continuous_test(self, interval=2):
        """Run continuous testing with data updates"""
        print(f"Starting continuous test with {interval}s intervals...")
        self.running = True
        
        try:
            while self.running:
                # Clear previous data
                self.debugger.send_radar([], [], [], [])
                self.debugger.send_simulate([], [], [])
                time.sleep(0.5)
                
                # Send new data
                self.send_all_data_types()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nStopping continuous test...")
            self.running = False
    
    def run_interactive_test(self):
        """Run interactive testing where user can choose what to send"""
        print("Interactive MQTT Tester")
        print("Available commands:")
        print("  1 - Send radar data")
        print("  2 - Send simulate data")
        print("  3 - Send antenna data")
        print("  4 - Send spectrogram")
        print("  5 - Send target figure")
        print("  6 - Send messages")
        print("  7 - Send all data")
        print("  8 - Clear all data")
        print("  q - Quit")
        
        while True:
            try:
                choice = input("\nEnter choice (1-8, q): ").strip().lower()
                
                if choice == 'q':
                    break
                elif choice == '1':
                    ids, azm, elv, colors = self.generate_fake_radar_data()
                    self.debugger.send_radar(ids, azm, elv, colors)
                elif choice == '2':
                    ids, azm, elv = self.generate_fake_simulate_data()
                    self.debugger.send_simulate(ids, azm, elv)
                elif choice == '3':
                    powers, received, selected = self.generate_fake_antenna_data()
                    self.debugger.send_antenna(powers, received, selected)
                elif choice == '4':
                    spec_fig = self.generate_fake_spectrogram()
                    self.debugger.send_spectrogram(spec_fig)
                elif choice == '5':
                    target_fig = self.generate_fake_target_figure()
                    self.debugger.send_pf(target_fig)
                elif choice == '6':
                    self.debugger.info("Info message from tester")
                    self.debugger.debug("Debug message from tester")
                    self.debugger.warning("Warning message from tester")
                    self.debugger.error("Error message from tester")
                elif choice == '7':
                    self.send_all_data_types()
                elif choice == '8':
                    self.debugger.send_radar([], [], [], [])
                    self.debugger.send_simulate([], [], [])
                    print("All data cleared")
                else:
                    print("Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                break
        
        print("Interactive test ended.")


def main():
    parser = argparse.ArgumentParser(description='MQTT Tester for UI Testing')
    parser.add_argument('--broker', default='127.0.0.1', help='MQTT broker address')
    parser.add_argument('--port', type=int, default=1884, help='MQTT broker port')
    parser.add_argument('--mode', choices=['single', 'continuous', 'interactive'], 
                       default='single', help='Test mode')
    parser.add_argument('--interval', type=int, default=2, 
                       help='Interval for continuous mode (seconds)')
    parser.add_argument('--quiet', action='store_true', help='Suppress verbose output')
    
    args = parser.parse_args()
    
    # Create tester
    tester = MqttTester(broker=args.broker, port=args.port, verbose=not args.quiet)
    
    try:
        if args.mode == 'single':
            print("Running single test...")
            tester.send_all_data_types()
        elif args.mode == 'continuous':
            tester.run_continuous_test(args.interval)
        elif args.mode == 'interactive':
            tester.run_interactive_test()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        print("Test completed.")


if __name__ == "__main__":
    main() 