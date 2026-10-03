import socket
import numpy as np
import time
import matplotlib.pyplot as plt
from collections import deque
from scipy.signal import butter, lfilter

# --- Configuration Constants ---
UDP_IP = "0.0.0.0"       # Listen on all network interfaces of the VM
UDP_PORT = 5500          # Port matching the router's stream destination
BUFFER_SIZE = 65536      # Socket receive buffer size

# Motion Detection Parameters
WINDOW_SIZE = 50         # Number of samples in the sliding window for variance calculation
THRESHOLD = 0.025        # Motion threshold value (adjust empirically)

# Real-time Plotting Parameters
MAX_HISTORY = 300        # Maximum data points displayed in the plot

# --- Data Structures for History ---
motion_metric_history = deque(maxlen=MAX_HISTORY)
time_history = deque(maxlen=MAX_HISTORY)
detection_history = deque(maxlen=MAX_HISTORY)

# --- Signal Processing Functions ---

def butter_lowpass_filter(data, cutoff, fs, order=5):
    """Applies a lowpass Butterworth filter to remove high-frequency noise."""
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    y = lfilter(b, a, data)
    return y

def decode_packet(raw_data):
    """
    Decodes the raw byte buffer into a complex CSI matrix.
    
    NOTE: Replace this placeholder implementation with your specific CSI-tool parser 
    (e.g., parsing headers and extracting I/Q values into a numpy array).
    """
    try:
        if len(raw_data) < 50:
            return None
        
        # Simulated structure: 3 antennas, 56 subcarriers (3, 56) complex matrix
        simulated_amplitude = 5 + 0.1 * np.random.randn(3, 56)
        simulated_phase = np.random.randn(3, 56)
        
        # Inject periodic movement simulation for visualization testing
        if len(motion_metric_history) % 100 < 20:
             simulated_amplitude += 1.5 * np.ones((3, 56)) 
             
        csi_matrix = simulated_amplitude * np.exp(1j * simulated_phase)
        return csi_matrix
    except Exception as error:
        print(f"Decoding error encountered: {error}")
        return None

# --- Real-Time Plot Setup ---
plt.ion() # Enable interactive mode for live plotting
fig, ax = plt.subplots(figsize=(12, 6))
line, = ax.plot([], [], label='Motion Metric (Standard Deviation)', color='blue')
ax.axhline(THRESHOLD, color='red', linestyle='--', label='Detection Threshold')
ax.set_title('Real-Time Human Presence Detection via CSI Variance')
ax.set_xlabel('Timestamp')
ax.set_ylabel('Amplitude Standard Deviation')
ax.legend()
ax.grid(True)

# --- Main Application Loop ---
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
        print(f"[*] Listening for raw router CSI streams on UDP {UDP_IP}:{UDP_PORT}...")
    except socket.error as socket_error:
        print(f"[-] Failed to bind socket: {socket_error}")
        return

    while True:
        try:
            data, address = sock.recvfrom(BUFFER_SIZE)
            current_timestamp = time.time()
            
            # Decode raw packet data
            csi_matrix = decode_packet(data)
            
            if csi_matrix is None:
                continue
                
            # Extract amplitude and select the primary antenna path
            amplitude = np.abs(csi_matrix)
            csi_path_data = amplitude[0, :]
            mean_amplitude = np.mean(csi_path_data)
            
            # Update metric history
            motion_metric_history.append(mean_amplitude)
            time_history.append(current_timestamp)
            
            # Perform detection computation once the sliding window is filled
            if len(motion_metric_history) >= WINDOW_SIZE:
                metric = np.std(list(motion_metric_history)[-WINDOW_SIZE:])
                is_detected = metric > THRESHOLD
                detection_history.append(is_detected)
                
                status_label = "MOTION DETECTED" if is_detected else "Idle"
                
                # Console Logging
                print(f"[{time.strftime('%H:%M:%S')}] Metric Value: {metric:.4f} | Status: {status_label}")

                # Update Live Plot
                line.set_xdata(time_history)
                line.set_ydata(motion_metric_history)
                ax.set_xlim(min(time_history), max(time_history))
                ax.set_ylim(min(motion_metric_history) * 0.9, max(motion_metric_history) * 1.1)
                
                fig.canvas.draw_idle()
                fig.canvas.flush_events()
                
            else:
                print(f"Buffering data: {len(motion_metric_history)}/{WINDOW_SIZE} samples collected.")

        except KeyboardInterrupt:
            print("\n[!] Program terminated by user.")
            break
        except Exception as general_error:
            # Catch loop-level anomalies to keep the stream listener alive
            continue

if __name__ == "__main__":
    main()
