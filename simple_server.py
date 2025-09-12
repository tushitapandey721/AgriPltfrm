from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Simple recovery guidelines
RECOVERY_GUIDELINES = {
    "drought": {
        "prevention": {
            "immediate": ["Install drip irrigation", "Apply mulch", "Plant drought-resistant varieties"],
            "long_term": ["Develop water management plan", "Install soil moisture monitoring"]
        },
        "immediate_response": ["Assess water availability", "Document damage", "Contact insurance"],
        "recovery": ["Replant drought-resistant varieties", "Improve soil organic matter"],
        "financial_aid": ["Government drought relief", "Crop insurance claims", "Emergency loans"]
    },
    "flood": {
        "prevention": {
            "immediate": ["Install drainage systems", "Create raised beds", "Build flood barriers"],
            "long_term": ["Develop flood management plan", "Install automated drainage"]
        },
        "immediate_response": ["Document flood damage", "Remove standing water", "Clear debris"],
        "recovery": ["Replant flood-tolerant varieties", "Improve soil drainage"],
        "financial_aid": ["Flood damage compensation", "Emergency assistance", "Infrastructure grants"]
    }
}

@app.route('/api/recovery/guidelines', methods=['GET'])
def get_recovery_guidelines():
    return jsonify({
        'success': True,
        'guidelines': RECOVERY_GUIDELINES
    })

@app.route('/api/recovery/guidelines/<calamity_type>', methods=['GET'])
def get_recovery_guidelines_by_type(calamity_type):
    if calamity_type in RECOVERY_GUIDELINES:
        return jsonify({
            'success': True,
            'calamity_type': calamity_type,
            'guidelines': RECOVERY_GUIDELINES[calamity_type]
        })
    else:
        return jsonify({'success': False, 'error': 'Calamity type not found'}), 404

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({
        'temperature': 25,
        'humidity': 60,
        'soil_moisture': 45,
        'calamities': [
            {
                'type': 'drought',
                'severity': 'moderate',
                'description': 'Low soil moisture detected',
                'timestamp': '2025-09-06T14:30:00Z',
                'recommended_action': 'Implement irrigation immediately'
            }
        ]
    })

@app.route('/api/calamities', methods=['GET'])
def get_calamities():
    return jsonify([
        {
            'type': 'drought',
            'severity': 'moderate',
            'description': 'Low soil moisture detected',
            'timestamp': '2025-09-06T14:30:00Z',
            'recommended_action': 'Implement irrigation immediately'
        }
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
