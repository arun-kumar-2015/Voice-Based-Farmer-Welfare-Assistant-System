from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Load data
with open("data.json") as f:
    database = json.load(f)

def detect_lang(text):
    if any(0x0C00 <= ord(c) <= 0x0C7F for c in text):
        return 'te'
    elif any(0x0900 <= ord(c) <= 0x097F for c in text):
        return 'hi'
    else:
        return 'en'

messages = {
    'te': {
        'rythu': "మీ రైతు బందు డబ్బులు {status}",
        'pm': "మీ పీఎం కిసాన్ డబ్బులు {status}",
        'unknown': "మీ ప్రశ్న అర్థం కాలేదు"
    },
    'hi': {
        'rythu': "आपका रायथु बंधु धन {status} हो गया है",
        'pm': "आपका पीएम किसान धन {status} हो गया है",
        'unknown': "आपका प्रश्न समझ नहीं आया"
    },
    'en': {
        'rythu': "Your Rythu Bandhu funds are {status}",
        'pm': "Your PM Kisan funds are {status}",
        'unknown': "I didn't understand your question"
    }
}

statuses = {
    'te': {'credited': 'క్రెడిట్ అయ్యాయి', 'pending': 'పెండింగ్ లో ఉంది'},
    'hi': {'credited': 'क्रेडिट हो गया है', 'pending': 'लंबित है'},
    'en': {'credited': 'credited', 'pending': 'pending'}
}

@app.route("/check", methods=["POST"])
def check_status():
    user_text = request.json["text"]
    lang = request.json["lang"].split('-')[0]  # e.g., 'te-IN' -> 'te'

    aadhaar = "123456789012"  # demo user

    farmer = None
    for f in database["farmers"]:
        if f["aadhaar"] == aadhaar:
            farmer = f

    if "రైతు బందు" in user_text or "రైతుబంధు" in user_text or "rythu" in user_text.lower() or "बंधु" in user_text or "bandhu" in user_text.lower():
        status = farmer["rythu_bandhu"]
        msg = messages[lang]['rythu'].format(status=statuses[lang][status])
    elif "పీఎం కిసాన్" in user_text or "కిసాన్" in user_text or "pm kisan" in user_text.lower() or "किसान" in user_text or "kisan" in user_text.lower():
        status = farmer["pm_kisan"]
        msg = messages[lang]['pm'].format(status=statuses[lang][status])
    else:
        msg = messages[lang]['unknown']

    lang_code = {'te': 'te-IN', 'hi': 'hi-IN', 'en': 'en-US'}[lang]

    return jsonify({"reply": msg, "lang": lang_code})

app.run(host='0.0.0.0', debug=True)

