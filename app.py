"""
Flask Backend untuk Sistem Pakar Identifikasi Kerusakan Mesin Industri
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from inference_engine import InferenceEngine
import os

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize inference engine
engine = InferenceEngine('knowledge_base.json', 'diagnosis_data.json')


@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Get all available symptoms"""
    try:
        symptoms = engine.get_symptoms_list()
        return jsonify({
            'success': True,
            'data': symptoms
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """Perform diagnosis based on selected symptoms"""
    try:
        data = request.get_json()
        selected_symptoms = data.get('symptoms', [])
        
        if not selected_symptoms:
            return jsonify({
                'success': False,
                'error': 'No symptoms selected'
            }), 400
        
        # Debug: print gejala yang dipilih
        print(f"DEBUG: Selected symptoms: {selected_symptoms}")
        
        diagnoses, reasoning = engine.forward_chaining(selected_symptoms)
        
        # Debug: print hasil
        print(f"DEBUG: Found {len(diagnoses)} diagnosis(es)")
        print(f"DEBUG: Reasoning steps: {len(reasoning)}")
        
        return jsonify({
            'success': True,
            'data': {
                'diagnoses': diagnoses,
                'reasoning': reasoning,
                'total_diagnoses': len(diagnoses)
            }
        })
    
    except Exception as e:
        import traceback
        print(f"ERROR: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/rules', methods=['GET'])
def get_rules():
    """Get all rules for explanation facility"""
    try:
        rules = []
        for rule in engine.rules:
            conditions = []
            for s in rule['if']:
                if s in engine.symptoms:
                    conditions.append(engine.symptoms[s]['name'])
            
            rules.append({
                'id': rule['id'],
                'description': rule['description'],
                'conditions': conditions,
                'conclusion': rule['then'],
                'cf': rule['cf']
            })
        
        return jsonify({
            'success': True,
            'data': rules
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Static file routes - must come after API routes
@app.route('/')
def index():
    """Serve static HTML file"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (CSS, JS, images)"""
    return send_from_directory('static', filename)


if __name__ == '__main__':
    # Create static directory if it doesn't exist
    os.makedirs('static', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

