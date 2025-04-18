import streamlit as st
import tempfile
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env and API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Page config
st.set_page_config(page_title="Audio Summarizer", layout="centered")
st.title("🎧 Audio Summarization App")

with st.expander("About"):
    st.write("""
    This app uses Google's Gemini API to transcribe and summarize audio files.
    Upload a `.mp3` or `.wav` file and choose your preferred summary style.
    """)

# Summary type selection
summary_type = st.selectbox("Choose Summary Style", ["Brief", "Detailed", "Bullet Points", "Action Items"])

prompt_map = {
    "Brief": "Give a short summary of this audio.",
    "Detailed": "Provide a detailed summary including key discussion points.",
    "Bullet Points": "Summarize the audio in bullet points.",
    "Action Items": "Extract action items from this audio."
}


def save_uploaded_file(uploaded_file):
    try:
        file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
        if file_extension not in ['.mp3', '.wav']:
            st.error("Only .mp3 and .wav files are allowed.")
            return None
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None


@st.cache_data
def summarize_audio(audio_file_path, prompt_text):
    try:
        model = genai.GenerativeModel("models/gemini-1.5-pro-latest")
        audio_file = genai.upload_file(path=audio_file_path)
        response = model.generate_content([prompt_text, audio_file])
        return response.text
    except Exception as e:
        return f" Error during summarization: {e}"


# Upload audio
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav"])

if audio_file is not None:
    audio_path = save_uploaded_file(audio_file)

    if audio_path:
        st.audio(audio_path)

        # Summarize
        if st.button("Summarize Audio"):
            with st.spinner("Summarizing... please wait"):
                summary_text = summarize_audio(audio_path, prompt_map[summary_type])
                st.success("Done!")
                st.subheader("Summary:")
                st.info(summary_text)

                # Allow download
                st.download_button("⬇️ Download Summary", summary_text, file_name="audio_summary.txt")
