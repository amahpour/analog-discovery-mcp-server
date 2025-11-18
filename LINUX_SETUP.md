# Linux Setup Guide

This guide covers the installation of Digilent WaveForms and its dependencies on Linux systems.

## Prerequisites

### Download Required Packages

Download the following packages from the [Digilent website](https://digilent.com/reference/software/waveforms/waveforms-3/start):

1. **Digilent Adept Runtime** (version 2.27.9 or later)
   - File: `digilent.adept.runtime_2.27.9-amd64.deb`
   
2. **Digilent WaveForms** (version 3.24.4 or later)
   - File: `digilent.waveforms_3.24.4_amd64.deb`

Save these files to your `~/Downloads` directory (or note the location for the installation steps).

## Installation Steps

### 1. Update Package Manager

```bash
sudo apt update
```

### 2. Install System Dependencies

Install the required Qt5 and system libraries:

```bash
sudo apt install -y xdg-utils \
                    libqt5multimedia5-plugins \
                    libqt5scripttools5 \
                    libqt5network5 \
                    libqt5serialport5
```

### 3. Install Digilent Adept Runtime

The Adept Runtime must be installed before WaveForms:

```bash
sudo dpkg -i ~/Downloads/digilent.adept.runtime_2.27.9-amd64.deb
```

If there are any dependency issues, fix them with:

```bash
sudo apt --fix-broken install -y
```

### 4. Install Digilent WaveForms

```bash
sudo dpkg -i ~/Downloads/digilent.waveforms_3.24.4_amd64.deb
```

If there are any remaining dependency issues:

```bash
sudo apt --fix-broken install -y
```

### 5. Verify Installation

Check that WaveForms is installed correctly:

```bash
waveforms --version
```

## WSL2 Setup (Windows Subsystem for Linux)

If you're running Linux on WSL2, you'll need to attach the Analog Discovery 2 USB device from Windows to your WSL environment using `usbipd-win`.

### 1. Install usbipd-win on Windows

Download and install `usbipd-win` from the [GitHub releases page](https://github.com/dorssel/usbipd-win/releases).

Alternatively, install via winget:

```powershell
winget install --interactive --exact dorssel.usbipd-win
```

### 2. List Connected USB Devices

Open PowerShell as Administrator and list all USB devices:

```powershell
usbipd list
```

Look for your Analog Discovery 2 device. It may appear as "USB Serial Converter" or similar. Note the BUSID (e.g., `5-4`).

Example output:
```
Connected:
BUSID  VID:PID    DEVICE                    STATE
5-4    0403:6014  USB Serial Converter      Not shared
```

### 3. Bind the Device

Bind the device to make it shareable with WSL:

```powershell
usbipd bind --busid 5-4
```

Replace `5-4` with your device's BUSID. This only needs to be done once; the binding persists across reboots.

### 4. Attach to WSL

Attach the device to your WSL distribution:

```powershell
usbipd attach --wsl --busid 5-4
```

Verify the device is attached:

```powershell
usbipd list
```

The device STATE should now show "Attached":
```
Connected:
BUSID  VID:PID    DEVICE                    STATE
5-4    0403:6014  USB Serial Converter      Attached
```

### 5. Verify in WSL

In your WSL terminal, verify the device is visible. The Analog Discovery 2 uses an FTDI FT232H chip (VID:PID `0403:6014`):

```bash
lsusb | grep 0403
```

You should see output similar to:
```
Bus 001 Device 004: ID 0403:6014 Future Technology Devices International, Ltd FT232H Single HS USB-UART/FIFO IC
```

### Notes

- The device must be attached each time you restart WSL or Windows
- Only one environment can use the device at a time (either Windows or WSL)
- To detach from WSL and use in Windows again: `usbipd detach --busid 5-4`
- The `--wsl` flag will automatically select your default WSL distribution

## Troubleshooting

### Permission Issues

If you encounter permission errors when accessing the Analog Discovery device, you may need to add your user to the appropriate group:

```bash
sudo usermod -a -G plugdev $USER
```

Then log out and log back in for the changes to take effect.

### USB Device Not Detected

If the device is not detected:

1. Check that the device is properly connected via USB (or attached via `usbipd` if using WSL)
2. Verify that the Adept Runtime is installed: `djtgcfg enum`
3. Check USB device visibility: `lsusb | grep 0403` (Analog Discovery 2 uses FTDI chip VID:PID 0403:6014)

### Missing Dependencies

If you encounter missing dependencies after installation, run:

```bash
sudo apt --fix-broken install -y
```

## Additional Resources

- [Digilent WaveForms Documentation](https://digilent.com/reference/software/waveforms/waveforms-3/start)
- [Analog Discovery Reference Manual](https://digilent.com/reference/test-and-measurement/analog-discovery-2/start)

