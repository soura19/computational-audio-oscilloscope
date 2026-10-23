import sounddevice as sd
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
from fractions import Fraction

GAIN1, GAIN2 = 2.0, 2.0
A1, A2 = 1.0, 1.0
delay_seconds = 1.5
samples = 2048
update_rate_ms = 20

devices = sd.query_devices()
valid_devices = []
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        name = dev['name']
        if not any(x in name for x in ["Mapper", "Primary", "DirectSound", "MME"]):
            valid_devices.append((i, name, dev['default_samplerate']))

device1 = next((d for d in valid_devices if "Microphone" in d[1]), None)
device2 = next((d for d in valid_devices if ("Headset" in d[1] or "Stereo Mix" in d[1]) and d != device1), None)

if not device2:
    device2 = next((d for d in valid_devices if d != device1), None)

(id1, name1, fs1) = device1
(id2, name2, fs2) = device2
fs1, fs2 = int(fs1), int(fs2)

data1 = np.zeros(samples)
data2 = np.zeros(samples)
delay1 = np.zeros(int(delay_seconds * fs1))
delay2 = np.zeros(int(delay_seconds * fs2))
norm1 = np.zeros(fs1)
norm2 = np.zeros(fs2)
freq_buf1 = np.zeros(fs1)
freq_buf2 = np.zeros(fs2)
f1_smooth, f2_smooth = 0, 0

def callback1(indata, frames, time, status):
    global data1, delay1, norm1, freq_buf1
    sig = indata[:, 0] * GAIN1
    
    norm1 = np.roll(norm1, -len(sig))
    norm1[-len(sig):] = sig
    m = np.max(np.abs(norm1))
    if m > 1e-6:
        sig = sig / m

    freq_buf1 = np.roll(freq_buf1, -len(sig))
    freq_buf1[-len(sig):] = sig

    combined = np.concatenate((delay1, sig))
    data1 = combined[:len(sig)]
    delay1 = combined[len(sig):]

def callback2(indata, frames, time, status):
    global data2, delay2, norm2, freq_buf2
    sig = indata[:, 0] * GAIN2
    
    norm2 = np.roll(norm2, -len(sig))
    norm2[-len(sig):] = sig
    m = np.max(np.abs(norm2))
    if m > 1e-6:
        sig = sig / m

    freq_buf2 = np.roll(freq_buf2, -len(sig))
    freq_buf2[-len(sig):] = sig

    combined = np.concatenate((delay2, sig))
    data2 = combined[:len(sig)]
    delay2 = combined[len(sig):]

stream1 = sd.InputStream(samplerate=fs1, device=id1, channels=1, callback=callback1, blocksize=samples)
stream2 = sd.InputStream(samplerate=fs2, device=id2, channels=1, callback=callback2, blocksize=samples)
stream1.start()
stream2.start()

def detect_freq(sig, fs):
    if np.max(np.abs(sig)) < 0.01:
        return 0, 0

    windowed = sig * np.hanning(len(sig))
    fft_data = np.fft.rfft(windowed)
    mag = np.abs(fft_data)
    freqs = np.fft.rfftfreq(len(sig), 1/fs)

    peak = np.argmax(mag[1:]) + 1
    total_energy = np.sum(mag[1:]**2)
    dominant_energy = 100 * (mag[peak]**2) / total_energy if total_energy > 0 else 0

    if 1 <= peak < len(mag)-1:
        alpha = mag[peak-1]
        beta  = mag[peak]
        gamma = mag[peak+1]
        denominator = alpha - 2*beta + gamma
        
        delta = 0.5 * (alpha-gamma) / denominator if abs(denominator) > 1e-12 else 0
        bin_width = freqs[1] - freqs[0]
        freq = freqs[peak] + delta*bin_width
    else:
        freq = freqs[peak]

    return freq, dominant_energy

def frequency_ratio(f1, f2, max_denominator=10):
    if f1 <= 0 or f2 <= 0:
        return "--"
    ratio = Fraction(f2 / f1).limit_denominator(max_denominator)
    return f"{ratio.denominator}:{ratio.numerator}"

def resample(sig, n):
    return np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(sig)), sig)

app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True)
win.resize(1200, 900)

plots, curves = [], []
titles = [
    ["Raw Signal (CH1)", "Reconstructed Signal (CH1)", "Residual Signal (CH1)"],
    ["Raw Signal (CH2)", "Reconstructed Signal (CH2)", "Residual Signal (CH2)"],
    ["Lissajous (Raw CH1 vs CH2)", "Lissajous (Reconstructed)", "Residual Comparison"]
]
y_labels = [
    ["Amplitude", "Amplitude", "Amplitude"],
    ["Amplitude", "Amplitude", "Amplitude"],
    ["CH2 Amplitude", "CH2 Amplitude", "CH2 Residual"]
]
x_labels = [
    ["Time (s)", "Time (s)", "Time (s)"],
    ["Time (s)", "Time (s)", "Time (s)"],
    ["CH1 Amplitude", "CH1 Amplitude", "CH1 Residual"]
]

for row in range(3):
    p_row, c_row = [], []
    for col in range(3):
        p = win.addPlot()
        c = p.plot()
        p.setYRange(-1, 1)
        p.showGrid(x=True, y=True)
        
        p.setTitle(titles[row][col])
        p.setLabel('left', y_labels[row][col])
        p.setLabel('bottom', x_labels[row][col])

        p_row.append(p)
        c_row.append(c)
        if col < 2:
            win.nextColumn()
    plots.append(p_row)
    curves.append(c_row)
    if row < 2:
        win.nextRow()

def update():
    global data1, data2, f1_smooth, f2_smooth

    t1 = np.arange(len(data1)) / fs1
    t2 = np.arange(len(data2)) / fs2

    f1_new, purity1 = detect_freq(freq_buf1, fs1)
    f2_new, purity2 = detect_freq(freq_buf2, fs2)

    f1_smooth = 0.9 * f1_smooth + 0.1 * f1_new
    f2_smooth = 0.9 * f2_smooth + 0.1 * f2_new
    ratio = frequency_ratio(f1_smooth, f2_smooth)

    s1 = A1 * np.sin(2*np.pi*f1_smooth*t1)
    s2 = A2 * np.sin(2*np.pi*f2_smooth*t2)

    n1 = data1 - s1
    n2 = data2 - s2

    d2r = resample(data2, len(data1))
    s2r = resample(s2, len(s1))
    n2r = resample(n2, len(n1))

    curves[0][0].setData(t1, data1)
    curves[0][1].setData(t1, s1)
    curves[0][2].setData(t1, n1)

    curves[1][0].setData(t2, data2)
    curves[1][1].setData(t2, s2)
    curves[1][2].setData(t2, n2)

    curves[2][0].setData(data1, d2r)
    curves[2][1].setData(s1, s2r)
    curves[2][2].setData(n1, n2r)

    win.setWindowTitle(f"CH1: {f1_smooth:.2f} Hz ({purity1:.1f}%) | CH2: {f2_smooth:.2f} Hz ({purity2:.1f}%) | Ratio: {ratio}")

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(update_rate_ms)

def cleanup():
    stream1.stop()
    stream2.stop()
    stream1.close()
    stream2.close()
    app.quit()

win.closeEvent = lambda event: cleanup()

try:
    app.exec()
finally:
    cleanup()
