# RT-AC68U CSI Room Monitoring Analyzer

This repository contains the backend Python application designed to receive, process, and analyze raw Channel State Information (CSI) streamed from a flashed **ASUS RT-AC68U** router (running custom firmware such as Nexmon-CSI or OpenWrt CSI Tool) to a virtual machine (Kali/Ubuntu). It calculates variance-based motion metrics to detect human presence and activity.

---

## Architecture Overview


```

[ ASUS RT-AC68U Router ] ---> (UDP Stream via LAN) ---> [ Kali / Ubuntu VM (Python Script) ]
│
(Calculates Amplitude & Rolling Variance)
│
▼
[ Real-time Plot / MQTT Output ]

```

---

## Step 1: Router Firmware & Setup

1. **Firmware**: Ensure your ASUS RT-AC68U is flashed with a compatible CSI-extracting firmware (e.g., Nexmon-CSI or OpenWrt CSI tool).
2. **Streaming Command**: Configure the router to stream raw UDP packets to your VM's static IP address and chosen port (default: `5500`).
   ```bash
   # Example command on the router side
   csi_logger --dst_ip <VM_IP_ADDRESS> --dst_port 5500
   ```

---

## Step 2: VM Environment Setup

1. Clone or download this repository onto your VM.
2. Install Python 3 and pip.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Step 3: Running the Application

Execute the receiver script to start listening for UDP streams, processing the frames, calculating motion metrics, and rendering the real-time monitoring graph:

```python
python3 src/csi_receiver.py
```

---
