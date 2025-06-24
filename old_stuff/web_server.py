from flask import Flask, render_template_string, Response
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
import threading
import queue
import time
from scipy import signal
from datetime import datetime
from plot_spectrogram import SpectrogramBuffer, plot_combined_spectrogram

app = Flask(__name__)
plot_queue = queue.Queue()
last_plot_data = None
last_update_time = None

# HTML template for the webpage
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>HackRF Spectrogram Viewer</title>
    <meta http-equiv="refresh" content="0.5">
    <style>
        body { background-color: #f0f0f0; }
        .plot-container { 
            margin: 20px;
            padding: 20px;
            background-color: white;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        img { max-width: 100%; }
        .update-time {
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="plot-container">
        <h2>Real-time Spectrogram</h2>
        {% if plot_data %}
            <img src="data:image/png;base64,{{ plot_data }}" alt="Spectrogram">
            <div class="update-time">Last updated: {{ update_time }}</div>
        {% else %}
            <p>Waiting for initial data...</p>
        {% endif %}
    </div>
</body>
</html>
"""

def create_plot(segments, sample_rates, center_freqs, titles, buffers):
    """Create a spectrogram plot and return it as a base64 encoded image"""
    fig = plot_combined_spectrogram(
        segments=segments,
        sample_rates=sample_rates,
        center_freqs=center_freqs,
        titles=titles,
        buffers=buffers
    )
    
    if fig is None:
        return None
    
    # Convert plot to base64
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    plot_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return plot_data

@app.route('/')
def index():
    global last_plot_data, last_update_time
    try:
        # Get the latest plot data from the queue
        last_plot_data = plot_queue.get_nowait()
        last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except queue.Empty:
        pass  # Keep using the last plot data
    
    return render_template_string(
        HTML_TEMPLATE, 
        plot_data=last_plot_data,
        update_time=last_update_time
    )

def run_web_server(host='0.0.0.0', port=5000):
    """Run the Flask web server"""
    app.run(host=host, port=port, debug=False)

def update_plot(segments, sample_rates, center_freqs, titles, buffers):
    """Update the plot data in the queue"""
    plot_data = create_plot(segments, sample_rates, center_freqs, titles, buffers)
    if plot_data:
        plot_queue.put(plot_data)

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
    
    # Start web server in a separate thread
    server_thread = threading.Thread(
        target=run_web_server,
        kwargs={'host': '10.0.4.93', 'port': 5000}
    )
    server_thread.daemon = True
    server_thread.start()
    
    print("Web server started at http://10.0.4.93:5000")
    print("Testing web plotting with synthetic data...")
    print("Press Ctrl+C to stop...")
    
    try:
        while True:
            # Update the plot with test data
            update_plot(
                segments=segments,
                sample_rates=[sample_rate] * len(segments),
                center_freqs=center_freqs,
                titles=[f"Test {i+1} - {fc/1e9:.1f} GHz" for i, fc in enumerate(center_freqs)],
                buffers=buffers
            )
            time.sleep(0.1)  # Update every 100ms
            
    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        print("Shutting down...") 