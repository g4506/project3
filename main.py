import os
import vertexai
from flask import Flask
from flask import Flask, render_template, request, send_from_directory
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, Part

app = Flask(__name__)

# Initialize Vertex AI
vertexai.init(project="my-project-3-453823", location="us-central1")
model = GenerativeModel("gemini-1.5-flash-001")

# GCS details
BUCKET_NAME = "my-project-3-453823_cloudbuild"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def list_gcs_files():
    """Fetch all `.wav` files from the GCS bucket."""
    client = storage.Client()
    blobs = client.list_blobs(BUCKET_NAME)
    return [blob.name for blob in blobs if blob.name.endswith(".wav")]

def download_from_gcs(filename):
    """Download the selected `.wav` file from GCS to the uploads folder."""
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    local_path = os.path.join(UPLOAD_FOLDER, filename)

    blob.download_to_filename(local_path)
    print(f"Downloaded {filename} to {local_path}")
    return local_path

def analyze_audio(filename):
    """Transcribe and analyze sentiment using Gemini API."""
    audio_file_uri = f"gs://{BUCKET_NAME}/{filename}"
    audio_part = Part.from_uri(audio_file_uri, mime_type="audio/x-wav")

    prompt_text = """
    Please provide an exact transcript for the audio, followed by sentiment analysis.

    Your response should follow the format:

    Text: USERS SPEECH TRANSCRIPTION

    Sentiment Analysis: positive|neutral|negative
    """
    prompt = Part.from_text(prompt_text)

    contents = [audio_part, prompt]
    response = model.generate_content(contents)

    result_text = response.text
    output_file = os.path.join(UPLOAD_FOLDER, "output.txt")

    with open(output_file, "w") as f:
        f.write(result_text)

    return result_text

@app.route("/")
def index():
    """Display all available `.wav` files from GCS."""
    files = list_gcs_files()
    return render_template("index.html", files=files)

@app.route("/process", methods=["GET"])
def process():
    """Process the selected `.wav` file."""
    filename = request.args.get("file")
    if not filename:
        return "No file selected", 400

    local_audio_path = download_from_gcs(filename)
    transcription_result = analyze_audio(filename)

    return render_template(
        "player.html",
        transcription=transcription_result,
        audio_file=filename
    )

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve the selected audio file."""
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Default to 8080
    app.run(host="0.0.0.0", port=port)
