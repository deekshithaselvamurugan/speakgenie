from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from routes.whisper_handler import transcribe_audio
from routes.gpt_handler import get_gpt_response
from routes.tts_handler import synthesize_speech
import os, json

app = Flask(__name__)
CORS(app)

@app.route('/api/voice-chat', methods=['POST'])
def voice_chat():
    audio = request.files['audio']
    audio.save("temp_audio.wav")
    transcript = transcribe_audio("temp_audio.wav")
    reply = get_gpt_response(transcript)
    audio_path = synthesize_speech(reply)
    return jsonify({
        "transcript": transcript,
        "response": reply,
        "audio_url": f"/api/audio/{os.path.basename(audio_path)}"
    })

@app.route('/api/text-chat', methods=['POST'])
def text_chat():
    user_input = request.json.get("message")
    reply = get_gpt_response(user_input)
    audio_path = synthesize_speech(reply)
    return jsonify({
        "response": reply,
        "audio_url": f"/api/audio/{os.path.basename(audio_path)}"
    })

@app.route('/api/roleplay/<scenario>', methods=['POST'])
def roleplay(scenario):
    user_input = request.json.get("message")
    path = f"scenarios/{scenario}.json"
    if not os.path.exists(path):
        return jsonify({"error": "Scenario not found"}), 404

    with open(path) as f:
        flow = json.load(f)

    for step in flow:
        expected = step.get("expected")
        if not expected or expected.lower().replace("*", "") in user_input.lower():
            reply = step["ai"]
            audio_path = synthesize_speech(reply)
            return jsonify({
                "response": reply,
                "audio_url": f"/api/audio/{os.path.basename(audio_path)}"
            })

    fallback = "Hmm, can you try again?"
    audio_path = synthesize_speech(fallback)
    return jsonify({
        "response": fallback,
        "audio_url": f"/api/audio/{os.path.basename(audio_path)}"
    })

@app.route('/api/audio/<filename>')
def get_audio(filename):
    return send_file(f"audio_responses/{filename}", mimetype="audio/mpeg")

if __name__ == '__main__':
    os.makedirs('audio_responses', exist_ok=True)
    app.run(debug=True)
