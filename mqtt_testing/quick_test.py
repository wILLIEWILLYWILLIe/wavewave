#!/usr/bin/env python3
"""
Quick test script to verify MQTT tester functionality
"""

import sys
import time

try:
    from mqtt_tester import MqttTester
    print("✓ MqttTester imported successfully")
except ImportError as e:
    print(f"✗ Failed to import MqttTester: {e}")
    sys.exit(1)

def quick_test():
    """Run a quick test to verify functionality"""
    print("Starting quick MQTT test...")
    
    try:
        # Create tester with localhost
        tester = MqttTester(broker="127.0.0.1", port=1884, verbose=True)
        print("✓ MqttTester created successfully")
        
        # Test radar data
        print("Testing radar data...")
        ids, azm, elv, colors = tester.generate_fake_radar_data(2)
        tester.debugger.send_radar(ids, azm, elv, colors)
        print(f"✓ Sent radar data: {ids}")
        
        # Test antenna data
        print("Testing antenna data...")
        powers, received, selected = tester.generate_fake_antenna_data()
        tester.debugger.send_antenna(powers, received, selected)
        print(f"✓ Sent antenna data: selected={selected}")
        
        # Test messages
        print("Testing messages...")
        tester.debugger.info("Quick test info message")
        tester.debugger.debug("Quick test debug message")
        print("✓ Sent test messages")
        
        # Wait a moment for messages to be sent
        time.sleep(1)
        
        print("✓ Quick test completed successfully!")
        print("Check your UI to see if the data appears correctly.")
        
    except Exception as e:
        print(f"✗ Quick test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1) 