#!/usr/bin/env python3
"""
Test script to verify Analog Discovery 2 MCP Server functionality
Run this after copying dwf.framework to /Library/Frameworks/
"""

import sys
sys.path.insert(0, '.')

from WF_SDK import device, scope, wavegen, error

def test_device_connection():
    """Test basic device connection"""
    print("=" * 60)
    print("TEST 1: Device Connection")
    print("=" * 60)
    try:
        device_data = device.open()
        print(f"✓ Device opened successfully!")
        print(f"  Name: {device_data.name}")
        print(f"  Version: {device_data.version}")
        print(f"  Analog Input Channels: {device_data.analog.input.channel_count}")
        print(f"  Analog Output Channels: {device_data.analog.output.channel_count}")
        print(f"  Max Buffer Size: {device_data.analog.input.max_buffer_size}")
        return device_data
    except error as e:
        print(f"✗ Failed to open device: {e}")
        return None

def test_scope_capture(device_data):
    """Test oscilloscope waveform capture"""
    print("\n" + "=" * 60)
    print("TEST 2: Oscilloscope Capture")
    print("=" * 60)
    try:
        # Initialize scope
        scope.open(device_data, 20e06, 0, 0.0, 5.0)
        print("✓ Scope initialized")
        
        # Capture from channel 1
        buffer = scope.record(device_data, 1)
        print(f"✓ Captured {len(buffer)} samples from channel 1")
        
        if len(buffer) > 0:
            print(f"  Sample range: {min(buffer):.6f}V to {max(buffer):.6f}V")
            print(f"  First 5 samples: {[f'{v:.6f}' for v in buffer[:5]]}")
        
        scope.close(device_data)
        print("✓ Scope closed")
        return True
    except error as e:
        print(f"✗ Scope test failed: {e}")
        return False

def test_waveform_generation(device_data):
    """Test waveform generator"""
    print("\n" + "=" * 60)
    print("TEST 3: Waveform Generator")
    print("=" * 60)
    try:
        # Generate sine wave on channel 1
        wavegen.generate(
            device_data,
            channel=1,
            function=wavegen.function.sine,
            offset=0.0,
            frequency=1000.0,
            amplitude=2.5
        )
        print("✓ Sine wave generated on channel 1")
        print("  Frequency: 1000 Hz")
        print("  Amplitude: 2.5 V")
        print("  Offset: 0.0 V")
        
        # Stop generation
        wavegen.close(device_data, 1)
        print("✓ Waveform generation stopped")
        return True
    except error as e:
        print(f"✗ Waveform generation failed: {e}")
        return False

def main():
    print("\nAnalog Discovery 2 MCP Server - Device Test")
    print("=" * 60)
    
    device_data = test_device_connection()
    if device_data is None:
        print("\n✗ Cannot proceed without device connection")
        return 1
    
    scope_ok = test_scope_capture(device_data)
    wavegen_ok = test_waveform_generation(device_data)
    
    # Close device
    device.close(device_data)
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Device Connection: ✓")
    print(f"Oscilloscope: {'✓' if scope_ok else '✗'}")
    print(f"Waveform Generator: {'✓' if wavegen_ok else '✗'}")
    
    if scope_ok and wavegen_ok:
        print("\n🎉 All tests passed! Your MCP server is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

