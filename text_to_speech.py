import requests

def run_tts_and_play(text):
    eleven_labs_api_key = '3baf281f748eae7ac30b4348424a2234'
    url = "https://api.elevenlabs.io/v1/text-to-speech/zrHiDhphv9ZnVXBqCLjz"

    headers = {
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

    output_filename = "reply.mp3"
    with open(output_filename, "wb") as output:
        output.write(response.content)
    return output_filename


