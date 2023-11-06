import requests
import simpleaudio as sa
from pydub import AudioSegment
from io import BytesIO

def run_tts_and_play(text):
    eleven_labs_api_key = '3baf281f748eae7ac30b4348424a2234'
    url = "https://api.elevenlabs.io/v1/text-to-speech/zrHiDhphv9ZnVXBqCLjz"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": eleven_labs_api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Make a POST request to the Eleven Labs API
    response = requests.post(url, json=data, headers=headers, stream=True)

    if response.status_code == 200:
        # Get the audio data from the response
        audio_data = response.content

        # Load the audio data into an AudioSegment
        audio = AudioSegment.from_file(BytesIO(audio_data), format="mp3")

        # Play the audio using simpleaudio
        play_obj = sa.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
        play_obj.wait_done()  # Wait for audio to finish playing
    else:
        print("Error: Failed to generate and play TTS audio.")

if __name__ == '__main__':
    run_tts_and_play(text='This is a test using Eleven Labs TTS')
