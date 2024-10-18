import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import speech_recognition as sr
import pyaudio
import wave
import numpy as np
import scipy.signal
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pygame
import os

class AudioRecorderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Audio Recorder and Transcriber")
        self.geometry("800x600")

        self.filename_var = tk.StringVar()
        self.duration_var = tk.IntVar(value=5)
        self.sample_rate_var = tk.IntVar(value=44100)
        self.chunk_size_var = tk.IntVar(value=1024)
        self.channels_var = tk.IntVar(value=1)
        self.transcription_var = tk.StringVar()

        self.fig, self.ax = plt.subplots()
        self.canvas = None
        self.playback_thread = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(expand=True, fill='both')

        recording_frame = ttk.LabelFrame(main_frame, text="Recording Settings")
        recording_frame.grid(row=0, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        filename_label = ttk.Label(recording_frame, text="Filename:")
        filename_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        filename_entry = ttk.Entry(recording_frame, textvariable=self.filename_var, width=30)
        filename_entry.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        filename_button = ttk.Button(recording_frame, text="Browse", command=self.browse_file)
        filename_button.grid(row=0, column=2, padx=5, pady=5)

        duration_label = ttk.Label(recording_frame, text="Duration (seconds):")
        duration_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        duration_scale = ttk.Scale(recording_frame, from_=1, to=10, variable=self.duration_var, orient='horizontal')
        duration_scale.grid(row=1, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        duration_value_label = ttk.Label(recording_frame, textvariable=self.duration_var)
        duration_value_label.grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)

        sample_rate_label = ttk.Label(recording_frame, text="Sample Rate:")
        sample_rate_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        sample_rate_scale = ttk.Scale(recording_frame, from_=22050, to=44100, variable=self.sample_rate_var, orient='horizontal')
        sample_rate_scale.grid(row=2, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        sample_rate_value_label = ttk.Label(recording_frame, textvariable=self.sample_rate_var)
        sample_rate_value_label.grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)

        chunk_size_label = ttk.Label(recording_frame, text="Chunk Size:")
        chunk_size_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        chunk_size_scale = ttk.Scale(recording_frame, from_=512, to=4096, variable=self.chunk_size_var, orient='horizontal')
        chunk_size_scale.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        chunk_size_value_label = ttk.Label(recording_frame, textvariable=self.chunk_size_var)
        chunk_size_value_label.grid(row=3, column=2, padx=5, pady=5, sticky=tk.W)

        channels_label = ttk.Label(recording_frame, text="Channels (1 for mono, 2 for stereo):")
        channels_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        channels_scale = ttk.Scale(recording_frame, from_=1, to=2, variable=self.channels_var, orient='horizontal')
        channels_scale.grid(row=4, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        channels_value_label = ttk.Label(recording_frame, textvariable=self.channels_var)
        channels_value_label.grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)

        record_button = ttk.Button(recording_frame, text="Start Recording", command=self.start_recording)
        record_button.grid(row=5, column=0, columnspan=3, pady=10)

        playback_frame = ttk.LabelFrame(main_frame, text="Playback")
        playback_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E))

        playback_button = ttk.Button(playback_frame, text="Play Recording", command=self.playback_recording)
        playback_button.pack(pady=10)

        stop_button = ttk.Button(playback_frame, text="Stop Playback", command=self.stop_playback)
        stop_button.pack(pady=10)

        upload_button = ttk.Button(playback_frame, text="Upload Audio", command=self.upload_audio)
        upload_button.pack(pady=10)

        transcription_frame = ttk.LabelFrame(main_frame, text="Transcription")
        transcription_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky=(tk.W, tk.E))

        result_label = ttk.Label(transcription_frame, text="Transcription:")
        result_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        transcription_text = tk.Text(transcription_frame, height=10, width=50, wrap=tk.WORD)
        transcription_text.grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.E))

        scrollbar = ttk.Scrollbar(transcription_frame, orient="vertical", command=transcription_text.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.NS, tk.E))
        transcription_text.config(yscrollcommand=scrollbar.set)

        self.transcription_text = transcription_text

    def browse_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Wave files", "*.wav")])
        if filename:
            self.filename_var.set(filename)

    def start_recording(self):
        filename = self.filename_var.get()
        duration = self.duration_var.get()
        sample_rate = self.sample_rate_var.get()
        chunk_size = self.chunk_size_var.get()
        channels = self.channels_var.get()

        record_thread = threading.Thread(target=self.record_and_transcribe, args=(filename, duration, sample_rate, chunk_size, channels))
        record_thread.start()

    def record_and_transcribe(self, filename, duration, sample_rate, chunk_size, channels):
        record_audio(filename, duration, sample_rate, chunk_size, channels)
        processed_filename = "processed_" + filename
        preprocess_audio(filename, processed_filename, sample_rate)
        transcription = analyze_audio(processed_filename)
        self.transcription_var.set(transcription)
        self.transcription_text.delete(1.0, tk.END)
        self.transcription_text.insert(tk.END, transcription)

        # Plot the waveform
        self.plot_waveform(processed_filename)

    def plot_waveform(self, filename):
        with wave.open(filename, 'rb') as wf:
            audio_data = wf.readframes(-1)
            audio_np = np.frombuffer(audio_data, dtype=np.int16)
            duration = wf.getnframes() / wf.getframerate()

        self.ax.clear()
        self.ax.plot(np.linspace(0, duration, len(audio_np)), audio_np)
        self.ax.set_title('Waveform')
        self.ax.set_xlabel('Time (s)')
        self.ax.set_ylabel('Amplitude')
        self.fig.tight_layout()

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def playback_recording(self):
        filename = self.filename_var.get()
        if os.path.exists(filename):
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
        else:
            messagebox.showerror("File Not Found", "The selected audio file does not exist.")

    def stop_playback(self):
        pygame.mixer.music.stop()

    def upload_audio(self):
        filename = filedialog.askopenfilename(filetypes=[("Wave files", "*.wav")])
        if filename:
            self.filename_var.set(filename)

            # Automatically start playing the uploaded audio
            self.playback_recording()

def record_audio(filename, duration=5, sample_rate=44100, chunk_size=1024, channels=1, format=pyaudio.paInt16):
    audio = pyaudio.PyAudio()
    
    stream = audio.open(format=format, channels=channels,
                        rate=sample_rate, input=True,
                        frames_per_buffer=chunk_size)
    
    print("Recording...")
    frames = []
    for i in range(0, int(sample_rate / chunk_size * duration)):
        data = stream.read(chunk_size)
        frames.append(data)
    print("Finished recording.")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    filepath = os.path.join(os.getcwd(), filename)
    
    with wave.open(filepath, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(sample_rate)
        wf.writeframes(b''.join(frames))

def preprocess_audio(input_filename, output_filename, sample_rate=44100):
    try:
        with wave.open(input_filename, 'rb') as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            n_frames = wf.getnframes()
            audio_data = wf.readframes(n_frames)

        audio_np = np.frombuffer(audio_data, dtype=np.int16)

        # Perform noise reduction using a simple high-pass filter
        b, a = scipy.signal.butter(1, 1000 / (0.5 * sample_rate), btype='high', analog=False)
        filtered_audio = scipy.signal.filtfilt(b, a, audio_np)

        filtered_audio = np.int16(filtered_audio)

        with wave.open(output_filename, 'wb') as wf:
            wf.setnchannels(n_channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(sample_rate)
            wf.writeframes(filtered_audio.tobytes())

            print(f"Audio processing completed: {output_filename}")
    except Exception as e:
        print(f"Error in audio processing: {e}")

def analyze_audio(filename):
    recognizer = sr.Recognizer()
    
    with sr.AudioFile(filename) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            print("Transcription:", text)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return "Could not understand audio"
        except sr.RequestError as e:
            print("Error occurred:", e)
            return f"Error occurred: {e}"

if __name__ == "__main__":
    app = AudioRecorderApp()
    app.mainloop()
