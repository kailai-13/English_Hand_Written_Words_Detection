from flask import Flask, render_template, request, jsonify
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import joblib
from tensorflow.keras.models import load_model

app = Flask(__name__)

# Load model and label encoder
model = load_model('model/best_model.keras')
label_encoder = joblib.load('model/label_encoder.pkl')

def preprocess_image(image):
    # Resize and convert to grayscale
    image = image.resize((32, 32)).convert('L')
    img_array = np.array(image) / 255.0
    img_array = img_array.reshape(1, 32, 32, 1)
    return img_array

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get image data from request
        data = request.get_json()
        image_data = data['image'].split(',')[1]  # Remove base64 header
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        
        # Preprocess and predict
        processed_image = preprocess_image(image)
        prediction = model.predict(processed_image)
        predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])
        
        return jsonify({'prediction': predicted_label[0]})
    
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)