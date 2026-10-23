# Computational Audio Oscilloscope for Real-Time Signal Analysis

Traditional digital storage oscilloscopes are essential for experimental physics but are often expensive and inaccessible outside formal laboratories. This project provides a low-cost, software-based alternative by utilizing standard consumer audio hardware to approximate the analytical capabilities of a dual-channel oscilloscope.

This project was originally presented at the Presision 2026 Science Exhibition (Team E) at Presidency University, Kolkata.

## The Computational Challenge
When using consumer hardware (like standard audio inputs or laptop microphones), ambient noise and hardware clock drift heavily distort the signal. Furthermore, applying standard Fast Fourier Transforms (FFT) on short time-domain buffers creates a severe quantization limit. For example, sampling at 44,100 Hz with a 2048-sample buffer strictly binds the frequency resolution to roughly 21.5 Hz per bin. A physically pure 400 Hz acoustic tone gets erroneously quantized, destroying the visual stability of the resulting Lissajous figures.

## The Solution
To bypass these hardware and computational limits, this framework uses a continuous, asynchronous digital signal processing pipeline:
*   **Hann Windowing:** Applied continuously to the incoming time-domain signal to smooth discrete buffer boundaries and suppress spectral leakage prior to FFT execution.
*   **Parabolic Peak Interpolation:** Instead of accepting discrete bins, the algorithm evaluates the peak magnitude and its neighbors. By calculating the fractional offset of the underlying parabola, it extracts the true acoustic frequency with sub-bin precision.
*   **Zero-Phase Reconstruction:** Once the exact frequency is extracted, the software dynamically renders a mathematically pure, zero-phase harmonic waveform. 
*   **Orthogonal Projection:** The reconstructed signals are mapped to perpendicular axes, translating microscopic temporal frequency errors into macroscopic geometric rotation.

## Technical Stack
*   **Language:** Python
*   **Audio Capture:** `sounddevice` (asynchronous capture via consumer ADCs)
*   **Mathematics:** `numpy`
*   **Visualization:** `pyqtgraph` (chosen for low-latency, hardware-accelerated UI rendering)

## Project Context
*   **Author:** Soura Tanay Roy (Undergraduate Physics, Presidency University, Kolkata)
*   **Mentor:** Dwaipayan Mukherjee
*   **Exhibition:** Presision 2026 Science Exhibition
*   **Poster:** [View the Presision 2026 Exhibition Poster Here](Presision-2026-Oscilloscope-Poster.pdf)

## Usage
To run this project locally, ensure you have Python 3 installed. 

1. Clone the repository.
2. Install the required dependencies: `pip install sounddevice numpy pyqtgraph PyQt6`
3. Run the application: `python oscilloscope.py`
4. The GUI will launch, actively analyzing your default system audio inputs to form the real-time Lissajous projections.

## License
This project is open-source and available under the MIT License.
