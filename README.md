# Audio Recorder and Transcriber
This is an audio recorder and transcriber application built using Python's Tkinter for the GUI, pyaudio for audio recording, and speech_recognition for transcription. It includes features for recording, playing back audio, uploading audio files, processing audio with noise reduction, and visualizing the waveform.

## Features
- Audio Recording: Record audio using the microphone with customizable settings (filename, duration, sample rate, chunk size, channels).
- Waveform Visualization: Visualize the recorded or uploaded audio waveform using matplotlib.
- Audio Playback: Play back the recorded or uploaded audio directly within the app.
- Audio Upload: Upload an existing .wav audio file for playback or transcription.
- Transcription: Automatically transcribe recorded or uploaded audio into text using Google Speech Recognition API.
- Noise Reduction: Preprocess the audio with a high-pass filter to reduce background noise.
- Requirements
- Python 3.x

## The following Python libraries:
- tkinter (Standard with Python)
- ttk (Standard with tkinter)
- pyaudio
- wave
- numpy
- scipy
- matplotlib
- speech_recognition
- pygame

You can install the dependencies using pip:

pip install pyaudio numpy scipy matplotlib speechrecognition pygame

# Usage

- Clone the repository:

  - [git clone https://github.com/Joderick-Sherwin/Speech-To-Text-Convertor](https://github.com/Joderick-Sherwin/Speech-To-Text-Convertor)

- Run the application:

  - python audio_recorder_transcriber.py

- In the app, you can:

  - Set the filename, duration, sample rate, chunk size, and number of channels for recording.
  - Record audio by clicking Start Recording.
  - Play back the audio using Play Recording.
  - Upload audio with the Upload Audio button for transcription.
  - Transcribe audio using the Transcribe Audio button.
  - Visualize the waveform of the audio in the graph section.
