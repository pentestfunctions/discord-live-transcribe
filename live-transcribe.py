import os
from vosk import Model, KaldiRecognizer
import pyaudio
import json  # Import json module to parse the JSON content

# Download model from here
# https://github.com/alphacep/vosk-space/blob/master/models.md
# Folder should look like english/am, english/conf, english/graph etc (change english to any model you want etc)

model_path = './english'
if not os.path.exists(model_path):
    print("Please download a model and specify the correct path.")
    exit(1)

model = Model(model_path)
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()

# List all available audio devices
print("Available audio input devices:")
for i in range(p.get_device_count()):
    dev_info = p.get_device_info_by_index(i)
    if dev_info['maxInputChannels'] > 0:
        print(f"Device {i}: {dev_info['name']} - Input Channels: {dev_info['maxInputChannels']}")

# Prompt user to select the device
mic_index = int(input("Enter the device index you want to use: "))

# Set up the audio stream with the selected device
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, input_device_index=mic_index, frames_per_buffer=8192)
stream.start_stream()

print("Recording started...")

# Open a text file for continuously updating with partial data
output_file_path = "partial_results.txt"
last_partial_text = ""

def format_text(text, max_words=14):
    """Split text into chunks of max_words and join with newlines."""
    words = text.split()
    chunks = [' '.join(words[i:i+max_words]) for i in range(0, len(words), max_words)]
    return '\n'.join(chunks)

while True:
    data = stream.read(4096, exception_on_overflow=False)
    if len(data) == 0:
        break
    if rec.AcceptWaveform(data):
        result = rec.Result()
        print(result)
    else:
        partial_json = rec.PartialResult()
        partial_data = json.loads(partial_json)
        partial_text = partial_data.get("partial", "")
        if partial_text and partial_text != last_partial_text:
            formatted_text = format_text(partial_text)
            with open(output_file_path, 'w') as file:
                file.write(formatted_text)
            last_partial_text = partial_text
            print(formatted_text)

stream.stop_stream()
stream.close()
p.terminate()
