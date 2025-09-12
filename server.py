from flask import Flask, jsonify, request
import requests
import random
from datetime import datetime, timedelta
import json
import time

app = Flask(__name__)

# --- CORS Configuration ---
# This is crucial for allowing your frontend to communicate with the backend.
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- API Keys ---
# You MUST replace these placeholder values with your actual API keys.
# 1. Get your OpenWeatherMap API key here: [https://openweathermap.org/api](https://openweathermap.org/api)
# 2. Get your Sentinel Hub API key here: [https://www.sentinel-hub.com/](https://www.sentinel-hub.com/)
OPENWEATHER_API_KEY = "171dec85082111c3023e7998d10f9af8"
SENTINEL_HUB_API_KEY = "eb5052d7-c609-4342-a755-6df5e2a348fd,iePvQA5vaR0R7PBQeSebPq5dOGYal2QV"

# The coordinates for your field (example location: India)
AOI_COORDS = [79.919, 21.054, 79.923, 21.058]
AOI_CENTER = [(AOI_COORDS[0] + AOI_COORDS[2]) / 2, (AOI_COORDS[1] + AOI_COORDS[3]) / 2]

# In-memory cache for latest sensor reading posted from IoT devices
latest_sensor_reading = {
    "data": None,
    "timestamp": None,
}

# Insurance data storage
insurance_policies = {}
calamity_events = []
privacy_settings = {
    "data_sharing": False,
    "analytics": True,
    "third_party": False
}

# Insurance types and terms
INSURANCE_TYPES = {
    "crop_insurance": {
        "name": "Crop Insurance",
        "coverage": ["Drought", "Flood", "Pest Attack", "Disease", "Hailstorm"],
        "premium_rate": 0.02,  # 2% of crop value
        "min_coverage": 10000,
        "max_coverage": 500000,
        "deductible": 0.1,  # 10% deductible
        "terms": [
            "Coverage applies to natural calamities and weather-related losses",
            "Minimum 75% crop damage required for claim",
            "Claim must be filed within 15 days of damage",
            "Assessment by government-approved surveyor required",
            "Premium must be paid before planting season"
        ]
    },
    "weather_insurance": {
        "name": "Weather-based Crop Insurance",
        "coverage": ["Rainfall deficit", "Excessive rainfall", "Temperature extremes"],
        "premium_rate": 0.015,
        "min_coverage": 5000,
        "max_coverage": 200000,
        "deductible": 0.15,
        "terms": [
            "Based on weather station data",
            "Automatic payout when weather parameters exceed thresholds",
            "No physical damage assessment required",
            "Coverage for specific weather events only"
        ]
    },
    "livestock_insurance": {
        "name": "Livestock Insurance",
        "coverage": ["Death due to disease", "Accidental death", "Theft"],
        "premium_rate": 0.03,
        "min_coverage": 20000,
        "max_coverage": 100000,
        "deductible": 0.05,
        "terms": [
            "Animals must be healthy at time of insurance",
            "Veterinary certificate required",
            "Death must be reported within 24 hours",
            "Post-mortem examination may be required"
        ]
    }
}

# --- Recovery Guidelines System ---
RECOVERY_GUIDELINES = {
    "drought": {
        "prevention": {
            "immediate": [
                "Install drip irrigation systems for water efficiency",
                "Apply mulch to retain soil moisture",
                "Plant drought-resistant crop varieties",
                "Implement water storage systems (tanks, ponds)"
            ],
            "long_term": [
                "Develop comprehensive water management plan",
                "Install soil moisture monitoring systems",
                "Create windbreaks to reduce evaporation",
                "Establish crop rotation with drought-tolerant species"
            ]
        },
        "immediate_response": [
            "Assess current water availability and crop condition",
            "Document damage with photos and measurements",
            "Contact insurance provider immediately",
            "Implement emergency irrigation if water available",
            "Remove severely damaged plants to conserve water"
        ],
        "recovery": [
            "Replant with drought-resistant varieties",
            "Improve soil organic matter content",
            "Install permanent irrigation infrastructure",
            "Implement water conservation techniques",
            "Monitor soil moisture regularly"
        ],
        "financial_aid": [
            "Government drought relief programs",
            "Crop insurance claims processing",
            "Emergency agricultural loans",
            "Water infrastructure grants",
            "Disaster assistance programs"
        ]
    },
    "flood": {
        "prevention": {
            "immediate": [
                "Install proper drainage systems",
                "Create raised beds for crops",
                "Build flood barriers around fields",
                "Monitor weather forecasts regularly"
            ],
            "long_term": [
                "Develop comprehensive flood management plan",
                "Install automated drainage systems",
                "Plant flood-tolerant crop varieties",
                "Create buffer zones near water bodies"
            ]
        },
        "immediate_response": [
            "Document flood damage with photos and videos",
            "Remove standing water immediately",
            "Clear debris from fields",
            "Contact insurance provider for claim filing",
            "Assess crop damage and survival rates"
        ],
        "recovery": [
            "Replant with flood-tolerant varieties",
            "Improve soil drainage and structure",
            "Implement flood-resistant farming techniques",
            "Install permanent drainage systems",
            "Monitor for disease outbreaks"
        ],
        "financial_aid": [
            "Flood damage compensation programs",
            "Emergency agricultural assistance",
            "Infrastructure repair grants",
            "Crop insurance flood coverage",
            "Disaster recovery loans"
        ]
    },
    "pest_attack": {
        "prevention": {
            "immediate": [
                "Implement Integrated Pest Management (IPM)",
                "Use biological control methods",
                "Practice crop rotation",
                "Maintain field hygiene and sanitation"
            ],
            "long_term": [
                "Develop comprehensive pest management strategy",
                "Install pest monitoring systems",
                "Create beneficial insect habitats",
                "Use resistant crop varieties"
            ]
        },
        "immediate_response": [
            "Identify pest species and damage extent",
            "Apply targeted treatment immediately",
            "Isolate affected areas to prevent spread",
            "Document damage for insurance claims",
            "Contact agricultural extension services"
        ],
        "recovery": [
            "Implement integrated pest management",
            "Restore beneficial insect populations",
            "Improve soil health and plant immunity",
            "Use biological control agents",
            "Monitor for pest resurgence"
        ],
        "financial_aid": [
            "Pest control subsidy programs",
            "Technical assistance grants",
            "Biological control funding",
            "Crop insurance pest coverage",
            "Research and development support"
        ]
    },
    "disease": {
        "prevention": {
            "immediate": [
                "Plant disease-resistant varieties",
                "Ensure proper plant spacing",
                "Maintain field sanitation",
                "Monitor weather conditions for disease risk"
            ],
            "long_term": [
                "Develop disease management protocols",
                "Implement crop rotation strategies",
                "Improve soil health and drainage",
                "Use disease forecasting systems"
            ]
        },
        "immediate_response": [
            "Identify disease type and severity",
            "Remove and destroy infected plants",
            "Apply appropriate fungicides/bactericides",
            "Document damage for insurance claims",
            "Quarantine affected areas"
        ],
        "recovery": [
            "Replant with disease-resistant varieties",
            "Improve soil health and drainage",
            "Implement proper crop rotation",
            "Use biological disease control",
            "Monitor for disease recurrence"
        ],
        "financial_aid": [
            "Disease control assistance programs",
            "Technical support services",
            "Research and development funding",
            "Crop insurance disease coverage",
            "Emergency response grants"
        ]
    },
    "hailstorm": {
        "prevention": {
            "immediate": [
                "Install hail nets over crops",
                "Build protective structures",
                "Monitor weather forecasts",
                "Plant hail-resistant varieties"
            ],
            "long_term": [
                "Develop comprehensive storm protection plan",
                "Install automated weather monitoring",
                "Create storm-resistant infrastructure",
                "Implement crop insurance coverage"
            ]
        },
        "immediate_response": [
            "Assess hail damage immediately",
            "Document damage with photos and measurements",
            "Treat plant wounds to prevent infection",
            "Contact insurance provider for claims",
            "Remove severely damaged plants"
        ],
        "recovery": [
            "Replant with storm-resistant varieties",
            "Implement protective measures",
            "Improve plant wound healing",
            "Monitor for secondary infections",
            "Strengthen storm protection systems"
        ],
        "financial_aid": [
            "Hail damage compensation programs",
            "Storm protection grants",
            "Emergency replanting assistance",
            "Crop insurance hail coverage",
            "Infrastructure improvement funding"
        ]
    }
}

# Calamity detection thresholds
CALAMITY_THRESHOLDS = {
    "drought": {"moisture": 20, "days_dry": 7},
    "flood": {"moisture": 90, "rainfall": 50},
    "pest_attack": {"humidity": 85, "temperature": 30},
    "disease": {"humidity": 80, "ndvi": 0.4},
    "hailstorm": {"temperature_drop": 10, "wind_speed": 25}
}

# --- Calamity Detection Logic ---
def detect_calamities(sensor_data, weather_data):
    """Detect potential calamities based on real-time data"""
    detected_calamities = []
    
    # Drought detection
    if sensor_data.get('soil_moisture', 0) < CALAMITY_THRESHOLDS['drought']['moisture']:
        detected_calamities.append({
            'type': 'drought',
            'severity': 'high' if sensor_data.get('soil_moisture', 0) < 15 else 'moderate',
            'description': 'Low soil moisture detected - drought conditions',
            'timestamp': datetime.utcnow().isoformat(),
            'recommended_action': 'Implement irrigation immediately'
        })
    
    # Flood detection
    if sensor_data.get('soil_moisture', 0) > CALAMITY_THRESHOLDS['flood']['moisture']:
        detected_calamities.append({
            'type': 'flood',
            'severity': 'high',
            'description': 'Excessive soil moisture - potential flooding',
            'timestamp': datetime.utcnow().isoformat(),
            'recommended_action': 'Drain excess water and protect crops'
        })
    
    # Pest attack detection
    if (sensor_data.get('air_humidity', 0) > CALAMITY_THRESHOLDS['pest_attack']['humidity'] and 
        sensor_data.get('air_temperature', 0) > CALAMITY_THRESHOLDS['pest_attack']['temperature']):
        detected_calamities.append({
            'type': 'pest_attack',
            'severity': 'moderate',
            'description': 'High humidity and temperature - favorable for pest growth',
            'timestamp': datetime.utcnow().isoformat(),
            'recommended_action': 'Apply pest control measures'
        })
    
    # Disease detection
    if (sensor_data.get('air_humidity', 0) > CALAMITY_THRESHOLDS['disease']['humidity'] and 
        sensor_data.get('ndvi', 0) < CALAMITY_THRESHOLDS['disease']['ndvi']):
        detected_calamities.append({
            'type': 'disease',
            'severity': 'high',
            'description': 'Low NDVI with high humidity - possible crop disease',
            'timestamp': datetime.utcnow().isoformat(),
            'recommended_action': 'Consult agricultural expert for disease treatment'
        })
    
    return detected_calamities

def calculate_insurance_premium(insurance_type, crop_value, risk_factors):
    """Calculate insurance premium based on type and risk factors"""
    base_premium = crop_value * INSURANCE_TYPES[insurance_type]['premium_rate']
    
    # Risk adjustment based on historical data and current conditions
    risk_multiplier = 1.0
    if risk_factors.get('high_risk_area', False):
        risk_multiplier += 0.2
    if risk_factors.get('previous_claims', 0) > 2:
        risk_multiplier += 0.3
    if risk_factors.get('crop_type_risk', 'low') == 'high':
        risk_multiplier += 0.15
    
    return base_premium * risk_multiplier

def assess_claim_eligibility(calamity_type, damage_percentage, policy_type):
    """Assess if a claim is eligible based on damage and policy terms"""
    if policy_type not in INSURANCE_TYPES:
        return False, "Invalid policy type"
    
    policy = INSURANCE_TYPES[policy_type]
    
    # Check if calamity is covered
    if calamity_type not in policy['coverage']:
        return False, f"{calamity_type} not covered under this policy"
    
    # Check minimum damage threshold
    min_damage = 75 if policy_type == 'crop_insurance' else 50
    if damage_percentage < min_damage:
        return False, f"Damage {damage_percentage}% below minimum threshold of {min_damage}%"
    
    return True, "Claim eligible"

# --- AI Prediction Logic ---
def run_ai_prediction(data):
    """
    This function contains the core AI prediction logic.
    In a more advanced version, this would be a trained machine learning model.
    """
    health_status = 'Healthy'
    risk_zone = 'Low'
    insurance_risk = 'Low'

    # Rule 1: High humidity and high temperature indicate a high pest risk
    if data['humidity'] > 80 and data['temperature'] > 28:
        risk_zone = 'High'
    elif data['humidity'] > 70 or data['temperature'] > 30:
        risk_zone = 'Moderate'

    # Rule 2: Low NDVI indicates a crop health issue
    if data['ndvi'] < 0.4:
        health_status = 'Critical'
    elif data['ndvi'] < 0.6:
        health_status = 'Stressed'

    # Rule 3: Crop insurance risk based on NDVI deviation from historical baseline
    # Simulating a historical baseline
    historical_baseline = 0.65
    historical_variance = 0.1
    if data['ndvi'] < (historical_baseline - historical_variance):
        insurance_risk = 'High'
    elif data['ndvi'] < historical_baseline:
        insurance_risk = 'Moderate'

    return {
        'health_status': health_status,
        'risk_zone': risk_zone,
        'insurance_risk': insurance_risk
    }

# --- Data Fetching Routes ---
@app.route('/api/data', methods=['GET'])
def get_agri_data():
    """
    A single API endpoint that fetches all data from external sources,
    runs the AI model, and returns a combined JSON response.
    """
    try:
        # Fetch real-time weather data
        weather_url = (
            f"https://api.openweathermap.org/data/2.5/weather?lat={AOI_CENTER[1]}"
            f"&lon={AOI_CENTER[0]}&units=metric&appid={OPENWEATHER_API_KEY}"
        )
        weather_response = requests.get(weather_url)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        current_temp = weather_data['main']['temp']
        current_humidity = weather_data['main']['humidity']
        
        # Fetch and process Sentinel-2 data (Simulated for this prototype for simplicity)
        # In a real-world scenario, you would make an API call to Sentinel Hub
        # to get the spectral data and calculate NDVI from it.
        # Example of Sentinel Hub Processing API call (simulated response):
        ndvi = 0.7 + (0.2 * (current_temp - 20) / 10) - (0.1 * (current_humidity - 70) / 20)
        if ndvi > 1: ndvi = 1
        if ndvi < 0.1: ndvi = 0.1

        # Prefer real sensor data if posted in last 10 minutes; otherwise simulate
        use_real_sensor = (
            latest_sensor_reading["data"] is not None
            and latest_sensor_reading["timestamp"] is not None
            and datetime.utcnow() - latest_sensor_reading["timestamp"] <= timedelta(minutes=10)
        )

        if use_real_sensor:
            moisture = float(latest_sensor_reading["data"].get("soil_moisture", 0))
        else:
            # Simulate sensor data influenced by real weather
            moisture = max(30, 60 - current_temp + (random.random() * 10 - 5))

        # Combine all data for AI prediction
        combined_data = {
            'temperature': current_temp,
            'humidity': current_humidity,
            'ndvi': ndvi,
            'moisture': moisture,
        }

        # Run the AI model
        prediction = run_ai_prediction(combined_data)
        
        # Detect calamities
        sensor_data = {
            'soil_moisture': moisture,
            'air_temperature': current_temp,
            'air_humidity': current_humidity,
            'ndvi': ndvi
        }
        weather_data = {
            'temperature': current_temp,
            'humidity': current_humidity
        }
        detected_calamities = detect_calamities(sensor_data, weather_data)
        
        # Store calamity events
        for calamity in detected_calamities:
            calamity_events.append(calamity)

        # Build the final response
        response = {
            'sensor_data': {
                'soil_moisture': moisture,
                'air_temperature': current_temp,
                'air_humidity': current_humidity,
                'source': 'iot' if use_real_sensor else 'simulated',
            },
            'satellite_data': {
                'ndvi': ndvi
            },
            'prediction': prediction,
            'calamities': detected_calamities,
            'insurance_risk': prediction.get('insurance_risk', 'Low')
        }
        
        return jsonify(response)

    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500


# --- IoT Sensor ingestion endpoints ---
@app.route('/api/sensor', methods=['POST', 'OPTIONS'])
def ingest_sensor():
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return ('', 204)

    payload = request.get_json(silent=True) or {}
    # Accept common keys: device_id, air_temperature, humidity, soil_moisture
    required_keys = {"soil_moisture", "air_temperature", "humidity"}
    if not required_keys.issubset(payload.keys()):
        return jsonify({'error': 'Missing required keys: soil_moisture, air_temperature, humidity'}), 400

    latest_sensor_reading["data"] = payload
    latest_sensor_reading["timestamp"] = datetime.utcnow()

    return jsonify({'status': 'ok', 'stored_at': latest_sensor_reading["timestamp"].isoformat()})


@app.route('/api/sensor/latest', methods=['GET'])
def latest_sensor():
    if latest_sensor_reading["data"] is None:
        return jsonify({'available': False})
    return jsonify({
        'available': True,
        'timestamp': latest_sensor_reading["timestamp"].isoformat(),
        'data': latest_sensor_reading["data"],
    })


# --- Insurance Management Endpoints ---
@app.route('/api/insurance/types', methods=['GET'])
def get_insurance_types():
    """Get available insurance types and their details"""
    return jsonify(INSURANCE_TYPES)

@app.route('/api/insurance/calculate-premium', methods=['POST'])
def calculate_premium():
    """Calculate insurance premium for given parameters"""
    data = request.get_json()
    insurance_type = data.get('type')
    crop_value = data.get('crop_value', 0)
    risk_factors = data.get('risk_factors', {})
    
    if insurance_type not in INSURANCE_TYPES:
        return jsonify({'error': 'Invalid insurance type'}), 400
    
    premium = calculate_insurance_premium(insurance_type, crop_value, risk_factors)
    policy = INSURANCE_TYPES[insurance_type]
    
    return jsonify({
        'premium': premium,
        'coverage_amount': crop_value,
        'deductible': crop_value * policy['deductible'],
        'net_payout': crop_value - (crop_value * policy['deductible']),
        'policy_details': policy
    })

@app.route('/api/insurance/policy', methods=['POST'])
def create_policy():
    """Create a new insurance policy"""
    data = request.get_json()
    policy_id = f"POL_{int(time.time())}"
    
    policy = {
        'id': policy_id,
        'farmer_id': data.get('farmer_id'),
        'insurance_type': data.get('type'),
        'crop_value': data.get('crop_value'),
        'premium': data.get('premium'),
        'coverage_start': data.get('coverage_start'),
        'coverage_end': data.get('coverage_end'),
        'status': 'active',
        'created_at': datetime.utcnow().isoformat()
    }
    
    insurance_policies[policy_id] = policy
    return jsonify({'policy_id': policy_id, 'status': 'created'})

@app.route('/api/insurance/claim', methods=['POST'])
def file_claim():
    """File an insurance claim"""
    data = request.get_json()
    policy_id = data.get('policy_id')
    calamity_type = data.get('calamity_type')
    damage_percentage = data.get('damage_percentage', 0)
    
    if policy_id not in insurance_policies:
        return jsonify({'error': 'Policy not found'}), 404
    
    policy = insurance_policies[policy_id]
    is_eligible, message = assess_claim_eligibility(
        calamity_type, damage_percentage, policy['insurance_type']
    )
    
    if is_eligible:
        claim_amount = policy['crop_value'] * (damage_percentage / 100) * (1 - INSURANCE_TYPES[policy['insurance_type']]['deductible'])
        claim = {
            'claim_id': f"CLM_{int(time.time())}",
            'policy_id': policy_id,
            'calamity_type': calamity_type,
            'damage_percentage': damage_percentage,
            'claim_amount': claim_amount,
            'status': 'approved',
            'filed_at': datetime.utcnow().isoformat()
        }
        return jsonify(claim)
    else:
        return jsonify({'error': message, 'eligible': False}), 400

@app.route('/api/calamities', methods=['GET'])
def get_calamities():
    """Get recent calamity events"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify(calamity_events[-limit:])

@app.route('/api/calamities/alert', methods=['POST'])
def create_calamity_alert():
    """Create a manual calamity alert"""
    data = request.get_json()
    alert = {
        'id': f"ALT_{int(time.time())}",
        'type': data.get('type'),
        'severity': data.get('severity', 'moderate'),
        'description': data.get('description'),
        'location': data.get('location'),
        'reported_by': data.get('farmer_id'),
        'timestamp': datetime.utcnow().isoformat(),
        'status': 'active'
    }
    calamity_events.append(alert)
    return jsonify(alert)

# --- Privacy Management Endpoints ---
@app.route('/api/privacy/settings', methods=['GET'])
def get_privacy_settings():
    """Get current privacy settings"""
    return jsonify(privacy_settings)

@app.route('/api/privacy/settings', methods=['POST'])
def update_privacy_settings():
    """Update privacy settings"""
    data = request.get_json()
    privacy_settings.update(data)
    return jsonify({'status': 'updated', 'settings': privacy_settings})

@app.route('/api/privacy/data-export', methods=['GET'])
def export_farmer_data():
    """Export farmer's data (GDPR compliance)"""
    farmer_id = request.args.get('farmer_id')
    if not farmer_id:
        return jsonify({'error': 'Farmer ID required'}), 400
    
    # In a real implementation, this would export all farmer's data
    export_data = {
        'farmer_id': farmer_id,
        'sensor_data': latest_sensor_reading,
        'policies': [p for p in insurance_policies.values() if p.get('farmer_id') == farmer_id],
        'calamities': [c for c in calamity_events if c.get('reported_by') == farmer_id],
        'exported_at': datetime.utcnow().isoformat()
    }
    return jsonify(export_data)

@app.route('/api/privacy/data-delete', methods=['DELETE'])
def delete_farmer_data():
    """Delete farmer's data (GDPR compliance)"""
    farmer_id = request.args.get('farmer_id')
    if not farmer_id:
        return jsonify({'error': 'Farmer ID required'}), 400
    
    # Remove farmer's policies
    policies_to_remove = [pid for pid, policy in insurance_policies.items() if policy.get('farmer_id') == farmer_id]
    for pid in policies_to_remove:
        del insurance_policies[pid]
    
    # Remove farmer's calamity events
    global calamity_events
    calamity_events = [c for c in calamity_events if c.get('reported_by') != farmer_id]
    
    return jsonify({'status': 'deleted', 'farmer_id': farmer_id})

# --- Farmer Feasibility Analysis ---
@app.route('/api/feasibility/analysis', methods=['GET'])
def get_feasibility_analysis():
    """Get feasibility analysis for local farmers"""
    return jsonify({
        'cost_benefit': {
            'average_premium': 1500,  # INR per acre
            'average_claim_payout': 15000,  # INR per acre
            'roi_percentage': 900,  # 900% ROI
            'break_even_months': 2
        },
        'accessibility': {
            'digital_literacy_required': 'Basic',
            'smartphone_required': True,
            'internet_required': True,
            'documentation_required': ['Aadhaar', 'Land Records', 'Bank Account']
        },
        'benefits': [
            'Financial protection against crop losses',
            'Access to credit with insurance backing',
            'Real-time monitoring and alerts',
            'Government subsidy support available',
            'Quick claim processing'
        ],
        'challenges': [
            'Initial premium payment',
            'Technology adoption',
            'Data privacy concerns',
            'Network connectivity in rural areas'
        ],
        'government_support': {
            'subsidy_percentage': 50,  # 50% premium subsidy
            'schemes': ['PMFBY', 'Weather-based Insurance', 'Crop Insurance'],
            'claim_settlement_days': 15
        }
    })

@app.route('/api/recovery/guidelines', methods=['GET'])
def get_recovery_guidelines():
    """Get recovery guidelines for all calamity types"""
    return jsonify({
        'success': True,
        'guidelines': RECOVERY_GUIDELINES,
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/recovery/guidelines/<calamity_type>', methods=['GET'])
def get_recovery_guidelines_by_type(calamity_type):
    """Get recovery guidelines for specific calamity type"""
    if calamity_type in RECOVERY_GUIDELINES:
        return jsonify({
            'success': True,
            'calamity_type': calamity_type,
            'guidelines': RECOVERY_GUIDELINES[calamity_type],
            'timestamp': datetime.utcnow().isoformat()
        })
    else:
        return jsonify({
            'success': False,
            'error': f'Calamity type "{calamity_type}" not found',
            'available_types': list(RECOVERY_GUIDELINES.keys())
        }), 404

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'time': datetime.utcnow().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)