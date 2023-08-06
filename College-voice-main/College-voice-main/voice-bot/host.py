import streamlit as st
import random
from voicebot import send_message
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from streamlit_lottie import st_lottie
import requests
import logging
import logging.handlers
import queue
import time
import urllib.request
from pathlib import Path
from typing import List
import numpy as np
import pydub

from streamlit_webrtc import WebRtcMode, webrtc_streamer


HERE = Path(__file__).parent

logger = logging.getLogger(__name__)


# This code is based on https://github.com/streamlit/demo-self-driving/blob/230245391f2dda0cb464008195a470751c01770b/streamlit_app.py#L48  # noqa: E501
def download_file(url, download_to: Path, expected_size=None):
    # Don't download the file twice.
    # (If possible, verify the download using the file length.)
    if download_to.exists():
        if expected_size:
            if download_to.stat().st_size == expected_size:
                return
        else:
            st.info(f"{url} is already downloaded.")
            if not st.button("Download again?"):
                return

    download_to.parent.mkdir(parents=True, exist_ok=True)

    # These are handles to two visual elements to animate.
    weights_warning, progress_bar = None, None
    try:
        weights_warning = st.warning("Downloading %s..." % url)
        progress_bar = st.progress(0)
        with open(download_to, "wb") as output_file:
            with urllib.request.urlopen(url) as response:
                length = int(response.info()["Content-Length"])
                counter = 0.0
                MEGABYTES = 2.0 ** 20.0
                while True:
                    data = response.read(8192)
                    if not data:
                        break
                    counter += len(data)
                    output_file.write(data)

                    # We perform animation by overwriting the elements.
                    weights_warning.warning(
                        "Downloading %s... (%6.2f/%6.2f MB)"
                        % (url, counter / MEGABYTES, length / MEGABYTES)
                    )
                    progress_bar.progress(min(counter / length, 1.0))
    # Finally, we remove these visual elements by calling .empty().
    finally:
        if weights_warning is not None:
            weights_warning.empty()
        if progress_bar is not None:
            progress_bar.empty()

def main():
    st.header("Real Time voicebot")

    # https://github.com/mozilla/DeepSpeech/releases/tag/v0.9.3
    MODEL_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.pbmm"  # noqa
    LANG_MODEL_URL = "https://github.com/mozilla/DeepSpeech/releases/download/v0.9.3/deepspeech-0.9.3-models.scorer"  # noqa
    MODEL_LOCAL_PATH = HERE / "models/deepspeech-0.9.3-models.pbmm"
    LANG_MODEL_LOCAL_PATH = HERE / "models/deepspeech-0.9.3-models.scorer"

    download_file(MODEL_URL, MODEL_LOCAL_PATH, expected_size=188915987)
    download_file(LANG_MODEL_URL, LANG_MODEL_LOCAL_PATH, expected_size=953363776)

    lm_alpha = 0.931289039105002
    lm_beta = 1.1834137581510284
    beam = 100

    sound_only_page = "Sound only (sendonly)"
    with_video_page = "Hrithik dev, sayani dev"
    app_mode = st.selectbox("Choose the app mode", [sound_only_page, with_video_page])

    if app_mode == sound_only_page:
        app_sst(
            str(MODEL_LOCAL_PATH), str(LANG_MODEL_LOCAL_PATH), lm_alpha, lm_beta, beam
        )




def app_sst(model_path: str, lm_path: str, lm_alpha: float, lm_beta: float, beam: int):
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
    )

    status_indicator = st.empty()

    if not webrtc_ctx.state.playing:
        return

    status_indicator.write("Loading...")
    text_output = st.empty()
    bot=st.empty()
    stream = None

    while True:
        if webrtc_ctx.audio_receiver:
            if stream is None:
                from deepspeech import Model

                model = Model(model_path)
                model.enableExternalScorer(lm_path)
                model.setScorerAlphaBeta(lm_alpha, lm_beta)
                model.setBeamWidth(beam)

                stream = model.createStream()

                status_indicator.write("Model loaded.")

            sound_chunk = pydub.AudioSegment.empty()
            try:
                audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=20)
            except queue.Empty:
                time.sleep(0.1)
                status_indicator.write("No frame arrived.")
                continue

            status_indicator.write("Running. Say something!")

            for audio_frame in audio_frames:
                sound = pydub.AudioSegment(
                    data=audio_frame.to_ndarray().tobytes(),
                    sample_width=audio_frame.format.bytes,
                    frame_rate=audio_frame.sample_rate,
                    channels=len(audio_frame.layout.channels),
                )
                sound_chunk += sound
               

            if len(sound_chunk) > 0:
                sound_chunk = sound_chunk.set_channels(1).set_frame_rate(
                    model.sampleRate()
                )
                buffer = np.array(sound_chunk.get_array_of_samples())
              
                stream.feedAudioContent(buffer)
                output_text=""
                text=""
                text = stream.intermediateDecode()
                output_text=text
                text_output.markdown(f"**User:** {text}")
                
                if output_text!="":
                    message=send_message(output_text)
                    bot.markdown(f'bot: {message}')
                    status_indicator.markdown("")
                    status_indicator.markdown("Say again")
                    time.sleep(5)
                    stream = model.createStream()

                    
                    
                else:
                    pass
              
                #ref.child(name_of_user).push().set(output_text)
                
                
                
        else:
            status_indicator.write("AudioReciver is not set. Abort.")
            break


r=random.randint(1,10000)
if not firebase_admin._apps:
    cred = credentials.Certificate('key.json')
    firebase_admin.initialize_app(cred,{'databaseURL': "https://college-48b1b-default-rtdb.firebaseio.com"})




ref = db.reference('question/')
#st.set_page_config(page_title="BOT",page_icon=":sound:")
r = random.random()
def load_lottieur(url):
    r = requests.get(url)
    if r.status_code !=200:
        return None
    return r.json()


lottie_coding =load_lottieur("https://assets3.lottiefiles.com/packages/lf20_ofa3xwo7.json")



question_list=[]
answers=[]

question_answers_dictionary={}

with st.container():

    st.subheader(":loudspeaker: ")
    st.markdown("<h1 style='text-align: center; color: Black;'>Hey! I am Here for helping you </h1>", unsafe_allow_html=True)
   # st.write("You can text here to know about JIS University.")
    
    left_column, right_column =st.columns(2) 
    with left_column:  
        name_of_user=st.text_input("Enter your name")
        question = st.text_input("Raise your voice through text typing: ")
        if question!="":
            message=send_message(question)
            st.write('bot: ',message)
            ref.child(name_of_user).push().set(question)
    with right_column:
        st_lottie(lottie_coding,width=200, height=200, key="coding")
#print(message)
#question_list.append(question)
#answers.append(message)
#question_answers_dictionary["question"]=question_list
#question_answers_dictionary["answers"]=answers
if __name__ == "__main__":
    import os

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
        "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)

    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)

    main()
