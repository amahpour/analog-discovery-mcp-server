# macOS WaveForms SDK Setup Guide

## Documentation Resources

### Official Documentation
- **SDK Location**: `/Applications/WaveForms.app/Contents/Resources/SDK/`
- **Reference Manual**: `/Applications/WaveForms.app/Contents/Resources/SDK/WaveForms SDK Reference Manual.pdf`
- **Python Samples**: `/Applications/WaveForms.app/Contents/Resources/SDK/samples/py/`

### Online Resources
- [WaveForms SDK Reference Manual](https://files.digilent.com/manuals/WaveFormsSDK/3.22.2/WaveForms%20SDK%20Reference%20Manual.pdf)
- [Digilent Forum - macOS Discussions](https://forum.digilent.com/)

## Current Status

### What's Working ✅
- WaveForms SDK library loads successfully
- SDK Version: 3.24.2 detected
- MCP server code is correct
- All 7 MCP tools properly registered
- Device is connected and visible to macOS (USB enumeration works)

### Current Issue ❌
- **Error**: ERC 3090 - "Adept NOK dmgrEnumDevicesEx"
- **Symptom**: SDK cannot enumerate devices despite device being connected
- **Status**: Known macOS/USB permissions issue

## Installation Requirements

According to Digilent documentation, on macOS you should:

1. **Install WaveForms.app** to `/Applications/`
2. **Copy dwf.framework** to `/Library/Frameworks/`

To copy the framework (requires sudo):
```bash
sudo cp -R /Applications/WaveForms.app/Contents/Frameworks/dwf.framework /Library/Frameworks/
```

**Note**: Your current setup loads the framework from the WaveForms.app bundle, which works for loading the library, but the `/Library/Frameworks/` location may be required for proper Adept Runtime initialization.

## Troubleshooting ERC 3090

### Possible Causes
1. **macOS USB Permissions**: Terminal/Python doesn't have USB access
2. **Framework Location**: dwf.framework not in `/Library/Frameworks/`
3. **macOS Security Settings**: System blocking unsigned frameworks
4. **Device State**: Device needs to be in specific state for SDK access

### Solutions to Try

#### 1. Copy Framework to System Location
```bash
sudo cp -R /Applications/WaveForms.app/Contents/Frameworks/dwf.framework /Library/Frameworks/
```

#### 2. Check USB Permissions
- **System Settings** → **Privacy & Security** → **USB Access**
- Ensure Terminal (or your Python executable) has USB access
- Grant access if prompted

#### 3. Check Security Settings
- **System Settings** → **Privacy & Security** → **General**
- Allow "App Store and identified developers"
- May need to click "Allow Anyway" for WaveForms/dwf.framework

#### 4. Try Running with Elevated Privileges
```bash
sudo python3 server.py
```

#### 5. Physical Troubleshooting
- Unplug and replug USB cable
- Try different USB port (USB 2.0 vs 3.0)
- Ensure WaveForms GUI is completely closed

#### 6. Verify Device in WaveForms GUI
- Open WaveForms.app
- Check Device Manager shows the device
- Close WaveForms completely before testing SDK

## Alternative: Using pydwf Package

As an alternative to the WF_SDK wrapper, you can use the `pydwf` package:

```bash
pip install pydwf
```

This provides a Python interface that wraps the Digilent C library and may handle macOS permissions differently.

## Testing

After implementing fixes, test with:
```bash
cd /Users/amahpour/code/analog-discovery-msp-server
python3 -c "from WF_SDK import device; d = device.open(); print(f'Success: {d.name}'); device.close(d)"
```

## References

- [WaveForms SDK Documentation](https://files.digilent.com/manuals/WaveForms/3.24.2/main.html)
- [Digilent Forum - macOS Topics](https://forum.digilent.com/)
- [pydwf Package](https://pypi.org/project/pydwf/)

