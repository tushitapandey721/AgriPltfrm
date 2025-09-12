from flask import Flask, jsonify
import json

app = Flask(__name__)

# Simple recovery guidelines for testing
RECOVERY_GUIDELINES = {
    "drought": {
        "prevention": {
            "immediate": ["Install drip irrigation", "Apply mulch"],
            "long_term": ["Develop water management plan"]
        },
        "immediate_response": ["Assess water availability", "Contact insurance"],
        "recovery": ["Replant drought-resistant varieties"],
        "financial_aid": ["Government relief programs"]
    }
}

@app.route('/api/recovery/guidelines', methods=['GET'])
def get_recovery_guidelines():
    return jsonify({
        'success': True,
        'guidelines': RECOVERY_GUIDELINES
    })

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        'temperature': 25,
        'humidity': 60,
        'soil_moisture': 45,
        'calamities': []
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
