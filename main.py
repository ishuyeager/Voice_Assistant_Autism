import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from io import BytesIO
import replicate
import os
from dotenv import load_dotenv
import base64
import requests
import time
import re

load_dotenv()

os.getenv("REPLICATE_API_TOKEN")

# Initialize the conversation
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


def cut_off_text(text, prompt):
    cutoff_phrase = prompt
    index = text.find(cutoff_phrase)
    if index != -1:
        return text[:index]
    else:
        return text


def generate_voice_response(user_input):
    new_prompt = """\
    You are a helpful, child therapist assistant at "Child Development & Treatment Centre" and honest. Always answer as helpfully as possible, while being safe and then you stop. The answer should be short, straight and to the point. If you don't know the answer to a question, please don't share false information."""

    llama_model = 'lucataco/llama-2-7b-chat:6ab580ab4eef2c2b440f2441ec0fc0ace5470edaf2cbea50b8550aec0b3fbd38'
    response = replicate.run(llama_model, input={"prompt": f"{new_prompt} {user_input} Assistant:", "top_p": 0.95,
                                                 "temperature": 0.1, "max_new_tokens": 500, "repetition_penalty": 1.1})
    final_outputs = cut_off_text(response, '</s>')
    return final_outputs


def generate_and_play_audio(text):
    # Fetch the audio data from Replicate API
    output = replicate.run(
        "awerks/neon-tts:139606fe1536f85a9f07d87982400b8140c9a9673733d47913af96738894128f",
        input={"text": text}
    )

    # Assuming the output is a string containing the audio file URL
    audio_url = output

    if audio_url:
        # Fetch the audio data as bytes
        response = requests.get(audio_url)
        audio_data = BytesIO(response.content)

        # Base64 encode the audio data
        audio_base64 = base64.b64encode(audio_data.read()).decode('utf-8')

        # Embed the audio in the HTML tag with autoplay
        audio_tag = f'<audio autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
        st.markdown(audio_tag, unsafe_allow_html=True)


def simulate_typing(message_placeholder, assistant_response):
    full_response = ""
    for chunk in re.split(r'(\s+)', assistant_response):
        full_response += chunk + " "
        time.sleep(0.1)

        # Add a blinking cursor to simulate typing
        message_placeholder.markdown(full_response)


sound = BytesIO()

placeholder = st.container()

placeholder.title("AutismCare Voice Assistant")
stt_button = Button(label='SPEAK', button_type='success', margin=(5, 5, 5, 5), width=100)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en';

    document.dispatchEvent(new CustomEvent("GET_ONREC", {detail: 'start'}));

    recognition.onspeechstart = function () {
        document.dispatchEvent(new CustomEvent("GET_ONREC", {detail: 'running'}));
    }
    recognition.onsoundend = function () {
        document.dispatchEvent(new CustomEvent("GET_ONREC", {detail: 'stop'}));
    }

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT,GET_ONREC",
    key="listen",
    refresh_on_update=False,
    override_height=40,
    debounce_time=0)

# Initialize user input in session state
if 'input' not in st.session_state:
    st.session_state.input = {'text': '', 'session': 0}

if result:
    if "GET_TEXT" in result:
        if result.get("GET_TEXT") != '' and result.get("GET_TEXT") != st.session_state.input['session']:
            st.session_state.input['text'] = result.get("GET_TEXT")
            st.session_state.input['session'] = result.get("GET_TEXT")

    if "GET_ONREC" in result:
        if result.get("GET_ONREC") == 'start':
            placeholder.image("mic.gif")
            st.session_state.input['text'] = ''
        elif result.get("GET_ONREC") == 'running':
            placeholder.image("mic.gif")
        elif result.get("GET_ONREC") == 'stop':
            if st.session_state.input['text'] != '':
                input_text = st.session_state.input['text']
                with st.chat_message("user"):
                    user_message_placeholder = st.empty()
                    simulate_typing(user_message_placeholder, input_text)

                response = generate_voice_response(input_text)
                st.write("**ChatBot:**")
                with st.spinner("Patience..."):
                    generate_and_play_audio(response)

                # Simulate typing the response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    simulate_typing(message_placeholder, response)

                # Add both user and assistant responses to chat history
                st.session_state.messages.append({"role": "user", "content": input_text})
                st.session_state.messages.append({"role": "assistant", "content": response})


# Display the conversation
st.write("**Conversation**")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


