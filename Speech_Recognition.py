import tkinter as tk
from tkinter import ttk, filedialog
import speech_recognition as sr
import pyaudio
import wave
import numpy as np
import scipy.signal

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
    
    with wave.open(filename, 'wb') as wf:
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
            print("Transcription:", text)  # Add debug print
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")  # Add debug print
            return "Could not understand audio"
        except sr.RequestError as e:
            print("Error occurred:", e)  # Add debug print
            return f"Error occurred: {e}"

def start_recording():
    filename = filename_entry.get()
    duration = int(duration_entry.get())
    sample_rate = int(sample_rate_entry.get())
    chunk_size = int(chunk_size_entry.get())
    channels = int(channels_entry.get())
    
    record_audio(filename, duration, sample_rate, chunk_size, channels)
    processed_filename = "processed_" + filename
    preprocess_audio(filename, processed_filename, sample_rate)
    
    result.set(f"Processed audio saved as {processed_filename}")
    transcribe_audio(processed_filename)

def transcribe_audio(filename):
    text = analyze_audio(filename)
    transcription.set(text)
    transcription_text.delete(1.0, tk.END)  # Clear previous text
    transcription_text.insert(tk.END, text)  # Display transcription in the text widget

# GUI setup
root = tk.Tk()
root.title("Audio Recorder and Transcriber")

mainframe = ttk.Frame(root, padding="10 10 20 20")
mainframe.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

filename_label = ttk.Label(mainframe, text="Filename:")
filename_label.grid(column=1, row=1, sticky=tk.W)
filename_entry = ttk.Entry(mainframe, width=30)
filename_entry.grid(column=2, row=1, sticky=(tk.W, tk.E))

duration_label = ttk.Label(mainframe, text="Duration (seconds):")
duration_label.grid(column=1, row=2, sticky=tk.W)
duration_entry = ttk.Entry(mainframe, width=30)
duration_entry.grid(column=2, row=2, sticky=(tk.W, tk.E))

sample_rate_label = ttk.Label(mainframe, text="Sample Rate:")
sample_rate_label.grid(column=1, row=3, sticky=tk.W)
sample_rate_entry = ttk.Entry(mainframe, width=30)
sample_rate_entry.grid(column=2, row=3, sticky=(tk.W, tk.E))

chunk_size_label = ttk.Label(mainframe, text="Chunk Size:")
chunk_size_label.grid(column=1, row=4, sticky=tk.W)
chunk_size_entry = ttk.Entry(mainframe, width=30)
chunk_size_entry.grid(column=2, row=4, sticky=(tk.W, tk.E))

channels_label = ttk.Label(mainframe, text="Channels (1 for mono, 2 for stereo):")
channels_label.grid(column=1, row=5, sticky=tk.W)
channels_entry = ttk.Entry(mainframe, width=30)
channels_entry.grid(column=2, row=5, sticky=(tk.W, tk.E))

record_button = ttk.Button(mainframe, text="Start Recording", command=start_recording)
record_button.grid(column=2, row=6, sticky=tk.W)

result = tk.StringVar()
result_label = ttk.Label(mainframe, textvariable=result, wraplength=300)
result_label.grid(column=1, row=7, columnspan=2, sticky=tk.W)

transcription_label = ttk.Label(mainframe, text="Transcription:")
transcription_label.grid(column=1, row=8, sticky=tk.W)

transcription = tk.StringVar()
transcription_text = tk.Text(mainframe, height=10, width=50, wrap=tk.WORD)
transcription_text.grid(column=1, row=9, columnspan=2, sticky=(tk.W, tk.E))
transcription_text.insert(tk.END, transcription.get())

for child in mainframe.winfo_children(): 
    child.grid_configure(padx=5, pady=5)

filename_entry.insert(0, "recorded_audio.wav")
duration_entry.insert(0, "5")
sample_rate_entry.insert(0, "44100")
chunk_size_entry.insert(0, "1024")
channels_entry.insert(0, "1")

root.mainloop()
