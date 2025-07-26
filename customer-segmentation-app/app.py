from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from flask_cors import CORS
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import joblib
import pandas as pd
import os

# --- 1. INITIALIZE FLASK APP ---
app = Flask(__name__)
app.secret_key = 'a-very-random-and-super-secret-key-for-this-project'
CORS(app)


# --- 2. IN-MEMORY USER STORE ---
users = {}


# --- 3. LOAD ML MODEL AND ARTIFACTS ---
MODEL_DIR = 'model'
MODEL_PATH = os.path.join(MODEL_DIR, 'catboost_model.pkl')
LABEL_ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder.pkl')
COLUMNS_PATH = os.path.join(MODEL_DIR, 'model_columns.pkl')

print("Loading model and artifacts...")
try:
    model = joblib.load(MODEL_PATH)
    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    model_columns = joblib.load(COLUMNS_PATH)
    print("Model and artifacts loaded successfully.")
except FileNotFoundError:
    print("CRITICAL: Model files not found. Please run the final model_training.py script.")
    model = None


# --- 4. HELPER FUNCTIONS & DECORATORS ---
def login_required(f):
    """Decorator to ensure a user is logged in before accessing a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('You must be logged in to view this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def run_prediction(data):
    """Preprocesses input data and returns a model prediction."""
    input_df = pd.DataFrame([data])
    
    # Preprocessing must match the final training script
    for col in ['Age', 'Work Experience', 'Family  Size']:
        input_df[col] = pd.to_numeric(input_df[col], errors='coerce')
    
    input_df['Age_Group'] = pd.cut(input_df['Age'], bins=[17, 25, 35, 50, 90], labels=['18-25', '26-35', '36-50', '51+'])
    input_df['Experience_Level'] = pd.cut(input_df['Work Experience'], bins=[-1, 2, 8, 20], labels=['Entry', 'Mid', 'Senior'])
    input_df['Career_Marital'] = input_df['Career'].astype(str) + '_' + input_df['Bachelor'].astype(str)
    
    live_df = pd.DataFrame(columns=model_columns)
    for col in model_columns:
        if col in input_df.columns:
            live_df[col] = input_df[col]
    
    categorical_features = ['Sex', 'Bachelor', 'Graduated', 'Career', 'Family Expenses', 'Variable', 'Age_Group', 'Experience_Level', 'Career_Marital']
    for col in categorical_features:
         if col in live_df.columns:
            live_df[col] = live_df[col].astype(str).fillna('missing')

    # model.predict() returns a 2D array like [['2']]
    prediction_encoded = model.predict(live_df)
    
    # CORRECTED LINE: .ravel() flattens the 2D array into a 1D array like ['2'], which is what the encoder expects.
    # This removes the DataConversionWarning.
    prediction_label = label_encoder.inverse_transform(prediction_encoded.ravel())[0]
    
    return prediction_label


# --- 5. AUTHENTICATION ROUTES ---
@app.route('/', methods=['GET'])
def root():
    """Redirects to login or dashboard based on session."""
    if 'email' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if 'email' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = users.get(email)
        
        if user and check_password_hash(user['password_hash'], password):
            session['email'] = email 
            session['name'] = user['name']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handles new user registration."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if email in users:
            flash('An account with this email already exists.', 'warning')
            return redirect(url_for('signup'))
        
        password_hash = generate_password_hash(password)
        users[email] = {'name': name, 'password_hash': password_hash}
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Clears the user session."""
    session.clear()
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('login'))


# --- 6. MAIN APPLICATION ROUTES (PROTECTED) ---
@app.route('/dashboard')
@login_required
def dashboard():
    """Serves the main dashboard page."""
    return render_template('index.html')

@app.route('/predict-persona')
@login_required
def predict_page():
    """Serves the prediction form page."""
    return render_template('predict.html')

@app.route('/leaderboard')
@login_required
def leaderboard_page():
    """Serves the leaderboard page."""
    return render_template('leaderboard.html')

@app.route('/contact')
@login_required
def contact_page():
    """Serves the contact page."""
    return render_template('contact.html')


# --- 7. API ENDPOINT FOR PREDICTION ---
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """Handles prediction requests from the frontend."""
    if model is None:
        return jsonify({'error': 'Model not loaded on the server.'}), 500
    try:
        data = request.get_json(force=True)
        prediction_label = run_prediction(data)
        return jsonify({'prediction': prediction_label})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'An error occurred during prediction.'}), 400


# --- 8. RUN THE APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)