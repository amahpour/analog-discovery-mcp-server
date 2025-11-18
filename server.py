#!/usr/bin/env python3
"""
MCP Server for Analog Discovery 2
Provides tools to interact with Digilent Analog Discovery 2 device via MCP protocol.
Uses the official WF_SDK wrapper from Digilent's WaveForms SDK Getting Started examples.
"""

import json
import sys
from time import sleep

from fastmcp import FastMCP

try:
    from WF_SDK import device, scope, wavegen, error
except ImportError as e:
    print(f"Error: WF_SDK not found. Please ensure WF_SDK is in the Python path.", file=sys.stderr)
    print(f"Details: {e}", file=sys.stderr)
    sys.exit(1)


# Initialize the FastMCP server
mcp = FastMCP("Analog Discovery 2 MCP Server")


class AnalogDiscoveryController:
    """Controller for Analog Discovery 2 device operations using WF_SDK."""
    
    def __init__(self):
        self.device_data = None
        self.scope_initialized = False
        self.wavegen_initialized = {}
    
    def connect(self, device_name: str = None, device_index: int = 0) -> dict:
        """Connect to an Analog Discovery 2 device.
        
        Args:
            device_name: Device name filter (None for first available, "Analog Discovery 2" for specific)
            device_index: Not used with WF_SDK, kept for API compatibility
        """
        try:
            if self.device_data is not None:
                self.disconnect()
            
            # Open device (None = first available, or specific name)
            device_filter = device_name if device_name else None
            self.device_data = device.open(device_filter)
            
            info = {
                "name": self.device_data.name,
                "version": self.device_data.version,
                "handle": self.device_data.handle.value if hasattr(self.device_data.handle, 'value') else str(self.device_data.handle),
            }
            
            return {"success": True, "info": info}
        except error as e:
            return {"error": f"Failed to connect: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to connect: {str(e)}"}
    
    def disconnect(self):
        """Disconnect from the device."""
        if self.device_data is not None:
            try:
                # Close instruments if initialized
                if self.scope_initialized:
                    scope.close(self.device_data)
                    self.scope_initialized = False
                
                for channel in list(self.wavegen_initialized.keys()):
                    wavegen.close(self.device_data, channel)
                    del self.wavegen_initialized[channel]
                
                # Close device
                device.close(self.device_data)
            except:
                pass
            self.device_data = None
    
    def ensure_connected(self) -> tuple[bool, str]:
        """Ensure device is connected, return (success, error_message)."""
        if self.device_data is None:
            result = self.connect()
            if "error" in result:
                return False, result["error"]
        return True, ""
    
    def capture_waveform(
        self,
        channel: int,
        sampling_frequency: float = 20e06,
        buffer_size: int = 0,
        offset: float = 0.0,
        amplitude_range: float = 5.0
    ) -> dict:
        """Capture analog waveform from specified channel (oscilloscope function).
        
        Args:
            channel: Channel number (1 or 2)
            sampling_frequency: Sampling frequency in Hz (default: 20MHz)
            buffer_size: Buffer size in samples (0 = maximum, default: 0)
            offset: Channel offset in volts (default: 0.0)
            amplitude_range: Channel range in volts (default: 5.0)
        """
        success, error_msg = self.ensure_connected()
        if not success:
            return {"error": error_msg}
        
        try:
            if channel not in [1, 2]:
                return {"error": "Channel must be 1 or 2 (WF_SDK uses 1-indexed channels)"}
            
            # Initialize scope if not already done
            if not self.scope_initialized:
                scope.open(self.device_data, sampling_frequency, buffer_size, offset, amplitude_range)
                self.scope_initialized = True
            
            # Record data from the channel
            buffer = scope.record(self.device_data, channel)
            
            # Get time axis
            time_data = []
            for index in range(len(buffer)):
                time_data.append(index / scope.data.sampling_frequency)
            
            # Limit returned data size for preview (first 1000 points)
            preview_size = min(1000, len(buffer))
            
            return {
                "success": True,
                "channel": channel,
                "sampling_frequency": scope.data.sampling_frequency,
                "samples": len(buffer),
                "time_data": time_data[:preview_size],
                "voltage_data": list(buffer[:preview_size]),
                "full_data_points": len(buffer),
            }
        except error as e:
            return {"error": f"Failed to capture analog: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to capture analog: {str(e)}"}
    
    def generate_waveform(
        self,
        channel: int,
        function: str,
        frequency: float,
        amplitude: float,
        offset: float = 0.0
    ) -> dict:
        """Generate waveform on specified channel.
        
        Args:
            channel: Channel number (1 or 2)
            function: Waveform type: sine, square, triangle, ramp_up, ramp_down, dc, noise, pulse, trapezium
            frequency: Frequency in Hz
            amplitude: Amplitude in volts
            offset: DC offset in volts (default: 0.0)
        """
        success, error_msg = self.ensure_connected()
        if not success:
            return {"error": error_msg}
        
        try:
            if channel not in [1, 2]:
                return {"error": "Channel must be 1 or 2 (WF_SDK uses 1-indexed channels)"}
            
            # Map function string to wavegen function constants
            function_map = {
                "sine": wavegen.function.sine,
                "square": wavegen.function.square,
                "triangle": wavegen.function.triangle,
                "ramp_up": wavegen.function.ramp_up,
                "ramp_down": wavegen.function.ramp_down,
                "dc": wavegen.function.dc,
                "noise": wavegen.function.noise,
                "pulse": wavegen.function.pulse,
                "trapezium": wavegen.function.trapezium,
            }
            
            if function.lower() not in function_map:
                return {"error": f"Function must be one of: {', '.join(function_map.keys())}"}
            
            func = function_map[function.lower()]
            
            # Generate waveform
            wavegen.generate(
                self.device_data,
                channel=channel,
                function=func,
                offset=offset,
                frequency=frequency,
                amplitude=amplitude
            )
            
            self.wavegen_initialized[channel] = True
            
            return {
                "success": True,
                "channel": channel,
                "function": function,
                "frequency": frequency,
                "amplitude": amplitude,
                "offset": offset,
            }
        except error as e:
            return {"error": f"Failed to generate waveform: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to generate waveform: {str(e)}"}
    
    def stop_waveform(self, channel: int) -> dict:
        """Stop waveform generation on specified channel.
        
        Args:
            channel: Channel number (1 or 2)
        """
        success, error_msg = self.ensure_connected()
        if not success:
            return {"error": error_msg}
        
        try:
            if channel not in [1, 2]:
                return {"error": "Channel must be 1 or 2 (WF_SDK uses 1-indexed channels)"}
            
            wavegen.close(self.device_data, channel)
            if channel in self.wavegen_initialized:
                del self.wavegen_initialized[channel]
            
            return {"success": True, "channel": channel, "status": "stopped"}
        except error as e:
            return {"error": f"Failed to stop waveform: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to stop waveform: {str(e)}"}


# Global controller instance
controller = AnalogDiscoveryController()


@mcp.tool()
def list_devices() -> str:
    """List all available Analog Discovery 2 devices connected to the system."""
    try:
        # WF_SDK doesn't have a direct list function, so we try to open the first device
        # to check if any are available
        try:
            test_device = device.open()
            device_count = 1  # At least one device found
            device.close(test_device)
            
            return json.dumps({
                "success": True,
                "device_count": device_count,
                "message": "At least one device found. Use connect_device to connect.",
            }, indent=2)
        except error as e:
            if "no connected devices" in str(e).lower():
                return json.dumps({
                    "success": True,
                    "device_count": 0,
                    "devices": [],
                }, indent=2)
            raise
    except Exception as e:
        return json.dumps({"error": f"Failed to list devices: {str(e)}"}, indent=2)


@mcp.tool()
def connect_device(device_name: str = None) -> str:
    """Connect to an Analog Discovery 2 device.
    
    Args:
        device_name: Device name filter (None for first available, "Analog Discovery 2" for specific)
    """
    result = controller.connect(device_name)
    return json.dumps(result, indent=2)


@mcp.tool()
def disconnect_device() -> str:
    """Disconnect from the current device."""
    controller.disconnect()
    return json.dumps({"success": True, "message": "Device disconnected"}, indent=2)


@mcp.tool()
def get_device_info() -> str:
    """Get information about the currently connected device."""
    if controller.device_data is None:
        return json.dumps({"error": "No device connected. Use connect_device first."}, indent=2)
    
    info = {
        "name": controller.device_data.name,
        "version": controller.device_data.version,
    }
    return json.dumps({"success": True, "info": info}, indent=2)


@mcp.tool()
def capture_waveform(
    channel: int,
    sampling_frequency: float = 20e06,
    buffer_size: int = 0,
    offset: float = 0.0,
    amplitude_range: float = 5.0
) -> str:
    """Capture analog waveform from a channel (oscilloscope function).
    
    Args:
        channel: Channel number (1 or 2)
        sampling_frequency: Sampling frequency in Hz (default: 20MHz)
        buffer_size: Buffer size in samples (0 = maximum, default: 0)
        offset: Channel offset in volts (default: 0.0)
        amplitude_range: Channel range in volts (default: 5.0)
    """
    result = controller.capture_waveform(channel, sampling_frequency, buffer_size, offset, amplitude_range)
    return json.dumps(result, indent=2)


@mcp.tool()
def generate_waveform(
    channel: int,
    function: str,
    frequency: float,
    amplitude: float,
    offset: float = 0.0
) -> str:
    """Generate waveform on a channel (waveform generator function).
    
    Args:
        channel: Channel number (1 or 2)
        function: Waveform type: sine, square, triangle, ramp_up, ramp_down, dc, noise, pulse, trapezium
        frequency: Frequency in Hz
        amplitude: Amplitude in volts
        offset: DC offset in volts (default: 0.0)
    """
    result = controller.generate_waveform(channel, function, frequency, amplitude, offset)
    return json.dumps(result, indent=2)


@mcp.tool()
def stop_waveform(channel: int) -> str:
    """Stop waveform generation on a channel.
    
    Args:
        channel: Channel number (1 or 2)
    """
    result = controller.stop_waveform(channel)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
