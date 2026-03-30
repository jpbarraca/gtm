from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import json
import sqlite3
import os

app = Flask(__name__)
DB_FILE = 'tones.db'

# --- Database Initialization ---
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS saved_tones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                music_style TEXT NOT NULL,
                guitar_type TEXT NOT NULL,
                pickup_type TEXT NOT NULL,
                tone_data TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Initialize DB on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

# --- Health Check for Hybrid PWA ---
@app.route('/api/status')
def status():
    return jsonify({"status": "ok", "mode": "server"})

def get_api_key():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            return config.get('api_key')
    except (FileNotFoundError, json.JSONDecodeError):
        return None

@app.route('/models', methods=['GET'])
def get_models():
    # Prioritize API key from the frontend request, fallback to config.json
    api_key = request.args.get('api_key') or get_api_key()
    
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return jsonify([{"name": "gemini-1.5-pro", "display_name": "API Key Missing (Default)"}])
    
    try:
        genai.configure(api_key=api_key)
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Strip 'models/' prefix if present for cleaner passing
                clean_name = m.name.replace('models/', '')
                available_models.append({
                    "name": clean_name,
                    "display_name": m.display_name
                })
        return jsonify(available_models)
    except Exception as e:
        return jsonify([{"name": "gemini-1.5-pro", "display_name": "Error loading models"}])

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    
    # Prioritize API key from the frontend request, fallback to config.json
    api_key = data.get('api_key') or get_api_key()
    
    guitar_type = data.get('guitar_type')
    pickup_type = data.get('pickup_type')
    music_style = data.get('music_style')
    model_name = data.get('model', 'gemini-1.5-pro')

    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        return jsonify({"error": "API Key is missing. Add it in Settings or config.json."}), 400
    if not music_style:
        return jsonify({"error": "Music style or player is missing."}), 400

    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Using the selected Gemini model
        model = genai.GenerativeModel(model_name)

        prompt = f"""
        You are a master-level guitar tone architect, audio engineer, and Guitarix (Linux) expert.

        Your task is to recreate the target tone: "{music_style}".
        The user is playing a {guitar_type} equipped with {pickup_type} pickups.

        Follow this systematic process (Research -> Apply -> Validate) before generating the final JSON:
        1. RESEARCH: Identify the core components of "{music_style}" (e.g., iconic amps, signature pedals, EQ curves, speaker types, mic placement).
        2. APPLY: Map these real-world components to their absolute closest equivalents in Guitarix. You MUST ONLY use real, existing Guitarix plugin names (e.g., GxTubeScreamer, GxFuzz, GxDistortion, GxCompressor, GxChorus, GxDelay, GxReverb, Tonestack, GxCabinet, GxAmplifier-X, JCM800 Preamp). DO NOT invent or hallucinate plugin names. If a specific boutique pedal doesn't exist, use the closest generic Gx equivalent.
        3. NAM FALLBACK: Critically evaluate if Guitarix's native amps are sufficient. If the tone requires a very specific, modern, or complex amplifier that Guitarix lacks, you MUST suggest using a NAM (Neural Amp Modeler) profile from Tone3000 / ToneHunt instead of a Guitarix Amp head.
        4. VALIDATE & TWEAK: Critically assess the user's gear ({guitar_type} with {pickup_type}). If they have bright single coils but want a dark humbucker tone, you MUST compensate by altering the Guitarix settings. Ensure gain staging logic holds up.

        You MUST return the output ONLY as a valid JSON object with the following strict structure:
        {{
            "recommended_pickup": "The optimal pickup selection (e.g., Neck, Bridge, Middle) for this specific tone.",
            "explanation": "A detailed explanation of how you adapted the classic '{music_style}' rig to work specifically with the user's {guitar_type} and {pickup_type}.",
            "nam_model_suggestion": {{
                "needed": true or false,
                "model_name": "If needed, the exact NAM model search query to look for on Tone3000/ToneHunt (e.g., 'Mesa Dual Rectifier Ch3 Modern'). Leave empty if false.",
                "reason": "Why a NAM model is recommended over native Guitarix amps for this specific tone."
            }},
            "chain": [
                {{
                    "name": "Exact Guitarix module name (e.g., GxFuzz, JCM800 Head, GxCabinet, or 'NAM Plugin Loader')",
                    "category": "Pre-FX, Drive, Amp, Cab, Modulation, or Time",
                    "active": true,
                    "settings": {{
                        "Param1": "Value1 (e.g., 6.5)",
                        "Param2": "Value2"
                    }}
                }}
            ],
            "tuning_considerations": [
                {{
                    "title": "A short, punchy title for the tip",
                    "icon": "A single relevant emoji (e.g., 🎚️, 🖐️, 📻)",
                    "description": "A detailed 2-sentence explanation of a playing technique, EQ trick, or gain staging tip specific to nailing THIS exact artist/style with the user's specific guitar."
                }}
            ]
        }}
        Ensure the JSON is perfectly formatted. Include 5 to 8 essential modules in the chain in sequential signal flow order, and provide exactly 3 tuning considerations.
        """

        # Generate JSON content
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json"
            )
        )

        # Parse and return to the frontend
        tone_data = json.loads(response.text)
        return jsonify(tone_data)

    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse the pedalboard data. The AI returned an invalid format."}), 500
    except Exception as e:
        return jsonify({"error": f"An error occurred with the AI service: {str(e)}"}), 500

# --- API Routes for Database ---

@app.route('/save', methods=['POST'])
def save_tone():
    data = request.json
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO saved_tones (music_style, guitar_type, pickup_type, tone_data)
                VALUES (?, ?, ?, ?)
            ''', (
                data.get('music_style'), 
                data.get('guitar_type'), 
                data.get('pickup_type'), 
                json.dumps(data.get('tone_data'))
            ))
            conn.commit()
        return jsonify({"status": "success", "message": "Rig saved to Tone Vault."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['GET'])
def search_tones():
    query = request.args.get('q', '').strip()
    try:
        with sqlite3.connect(DB_FILE) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            if query:
                search_term = f'%{query}%'
                c.execute('''
                    SELECT * FROM saved_tones 
                    WHERE music_style LIKE ? OR guitar_type LIKE ? OR pickup_type LIKE ?
                    ORDER BY created_at DESC
                ''', (search_term, search_term, search_term))
            else:
                c.execute('SELECT * FROM saved_tones ORDER BY created_at DESC LIMIT 10')
            
            rows = c.fetchall()
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "music_style": row["music_style"],
                    "guitar_type": row["guitar_type"],
                    "pickup_type": row["pickup_type"],
                    "tone_data": json.loads(row["tone_data"]),
                    "created_at": row["created_at"]
                })
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete/<int:tone_id>', methods=['DELETE'])
def delete_tone(tone_id):
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('DELETE FROM saved_tones WHERE id = ?', (tone_id,))
            conn.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')
