Driver Drowsiness Detection & Alert System

A real-time computer vision and embedded hardware integration project that detects prolonged eye closure and generates a physical alert using an ESP32.

Overview

This project uses a webcam and MediaPipe Face Mesh to detect facial landmarks and calculate the Eye Aspect Ratio (EAR) for monitoring eye openness.

To account for differences between users, the system performs an initial calibration to calculate a personalized baseline EAR and derives an eye-closure threshold from it.

The system also analyzes consecutive frames to distinguish a normal blink from prolonged eye closure. When prolonged eye closure is detected, the Python application communicates with an ESP32 through serial communication, which activates an LED and buzzer as an alert.

System Flow

Webcam
↓
MediaPipe Face Mesh
↓
Eye Landmarks
↓
EAR Calculation
↓
Calibration & Baseline
↓
Eye-Closure Threshold
↓
Consecutive-Frame Analysis
↓
Prolonged Eye Closure
↓
Serial Communication
↓
ESP32
↓
LED + Buzzer Alert

Technologies Used
Python
OpenCV
MediaPipe
ESP32
Embedded C/C++
Serial Communication
Key Features
Real-time facial landmark detection
Eye Aspect Ratio (EAR) calculation
Personalized calibration
Baseline-based eye-closure threshold
Consecutive-frame analysis to reduce false alerts from normal blinking
Python–ESP32 serial communication
LED and buzzer hardware alert
Hardware
ESP32
LED
Active buzzer
Breadboard
Jumper wires
Future Improvements
Yawning detection
Head-pose estimation
PERCLOS-based drowsiness analysis
Improved false-positive handling
More comprehensive driver monitoring.
