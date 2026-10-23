# Python Audio Oscilloscope

A Python script that uses standard consumer audio inputs (two microphones connected to the pc, wired/wireless) to act as a dual-channel oscilloscope. It processes audio in real-time to generate and visualize stable Lissajous figures.

## The Problem
Plotting Lissajous figures from raw consumer audio usually fails. Background noise and hardware clock drift distort the signal. Worse, running a standard FFT on short audio buffers (e.g., 2048 samples at 44.1kHz) restricts frequency resolution to about ~21.5 Hz per bin. That means a pure 400 Hz tone gets quantized, destroying the visual stability of the projection.

## How It Works
Instead of plotting the noisy raw data, this script actively processes and reconstructs the signal in real-time:
1. **Windowing & FFT:** Applies continuous Hann windowing to the incoming audio to stop spectral leakage.
2. **Sub-Bin Interpolation:** Uses parabolic peak interpolation to calculate the exact frequency between standard FFT bins.
3. **Signal Reconstruction:** Generates clean, zero-phase sine waves using those exact detected frequencies.
4. **Real-Time Plotting:** Maps the reconstructed signals to X and Y axes to display clean Lissajous figures alongside the raw, noisy hardware input.

## Tech Stack
* **Python 3**
* **`sounddevice`:** Asynchronous audio capture
* **`numpy`:** Signal processing and interpolation math
* **`pyqtgraph`:** Hardware-accelerated GUI plotting

## Run It Locally
1. Clone this repository.
2. Install the required dependencies: 
   `pip install sounddevice numpy pyqtgraph PyQt6`
3. Run the script: 
   `python oscilloscope.py`
*(Note: Ensure you have two active independent audio input connected to your system).*
4. Now install an audio frequency generator app from PlayStore/AppStore on two smartphones, and point their speaker to each audio channel.
5. Generate random frequency ratio (e.g. one phone can generate a frequency of 200Hz while other can generate 400Hz), and watch it getting detected by the program in the title bar while also drawing the appropriate lissajous figures.

---
*Built for the Presision 2026 Science Exhibition at Presidency University, Kolkata.*
*Mentor: Dwaipayan Mukherjee*
*[View the original exhibition poster here](Presision%202026%20Oscilloscope%20Poster.pdf)*
