# MQTT Tester

A comprehensive tool to send fake data to test the UI functionality of the wavewave application.

## Features

- **Radar Data**: Send fake radar target data with random positions and colors
- **Simulation Data**: Send fake simulation data (marked with negative IDs)
- **Antenna Data**: Send fake antenna power and received data for 16 antennas
- **Spectrogram**: Generate and send fake spectrogram images
- **Target Figures**: Generate and send fake target detection plots
- **Messages**: Send various types of log messages (info, debug, warning, error)

## Installation

1. Install the required dependencies:
```bash
pip install -r mqtt_tester_requirements.txt
```

## Usage

### Basic Usage

Run a single test that sends all data types:
```bash
python mqtt_tester.py
```

### Command Line Options

```bash
python mqtt_tester.py [OPTIONS]
```

Options:
- `--broker BROKER`: MQTT broker address (default: 127.0.0.1)
- `--port PORT`: MQTT broker port (default: 1883)
- `--mode {single,continuous,interactive}`: Test mode (default: single)
- `--interval INTERVAL`: Interval for continuous mode in seconds (default: 2)
- `--quiet`: Suppress verbose output

### Test Modes

#### 1. Single Mode (default)
Sends all data types once and exits:
```bash
python mqtt_tester.py --mode single
```

#### 2. Continuous Mode
Continuously sends data with specified intervals:
```bash
python mqtt_tester.py --mode continuous --interval 5
```

#### 3. Interactive Mode
Interactive menu where you can choose what to send:
```bash
python mqtt_tester.py --mode interactive
```

Interactive menu options:
- `1` - Send radar data
- `2` - Send simulate data
- `3` - Send antenna data
- `4` - Send spectrogram
- `5` - Send target figure
- `6` - Send messages
- `7` - Send all data
- `8` - Clear all data
- `q` - Quit

### Examples

1. Test with a remote MQTT broker:
```bash
python mqtt_tester.py --broker 192.168.1.100 --port 1883
```

2. Run continuous testing with 3-second intervals:
```bash
python mqtt_tester.py --mode continuous --interval 3
```

3. Run interactive testing with quiet mode:
```bash
python mqtt_tester.py --mode interactive --quiet
```

## Data Types

### Radar Data
- Target IDs: TARGET_01, TARGET_02, etc.
- Azimuth: 0-360 degrees
- Elevation: 0-90 degrees
- Colors: Random hex colors

### Simulation Data
- Target IDs: -SIM_01, -SIM_02, etc. (negative prefix)
- Azimuth: 0-360 degrees
- Elevation: 0-90 degrees

### Antenna Data
- 16 antennas (0-15)
- Power values: -30 to 10 dBm
- Received values: 0-10 (arbitrary units)
- Selected antennas: 2-4 randomly selected

### Messages
- Info: System status messages
- Debug: Processing information
- Warning: System warnings
- Error: Error messages

## Troubleshooting

1. **Connection Failed**: Make sure the MQTT broker is running and accessible
2. **Import Errors**: Install the required dependencies
3. **Permission Errors**: Make sure you have write permissions for the current directory

## Notes

- The tester generates random data each time it runs
- Images (spectrograms and target figures) are generated using matplotlib
- All data is sent in JSON format as expected by the UI
- The tester automatically clears previous data before sending new data in continuous mode 