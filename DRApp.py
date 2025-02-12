from flask import Flask, request, jsonify, render_template
import tensorflow as tf
import efficientnet
import os
import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.utils import get_custom_objects
from keras.layers import Activation # This import is unused

# Instead of importing FixedDropout, define it directly if it is not available in newer versions of efficientnet
from tensorflow.keras.layers import Dropout

class FixedDropout(Dropout):
    def _get_noise_shape(self, inputs):
        if self.noise_shape is None:
            return self.noise_shape

        symbolic_shape = tf.shape(inputs)
        noise_shape = [symbolic_shape[axis] if shape is None else shape
                       for axis, shape in enumerate(self.noise_shape)]
        return tuple(noise_shape)


# Define swish activation function if needed
@tf.keras.utils.register_keras_serializable()
def swish(x):
    return tf.nn.swish(x)

get_custom_objects().update({'swish': swish, 'FixedDropout': FixedDropout})  # Add FixedDropout to custom_objects


# Initialize Flask app
app = Flask(__name__)

# Load the model
model_path = "./model/model_gaussian.keras"
model = load_model(model_path, custom_objects=get_custom_objects())  # Pass get_custom_objects() to load_model

# Configure upload folder
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Define input image size for the model
IMAGE_SIZE = (224, 224)  # Update based on your model's input size

# Routes
@app.route('/')
def index():
    return render_template('index.html')


def predict():
    categories = ["NOT PRESENT", "MILD", "MODERATE", "SEVERE", "PROLIFERATE"]
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return ({"error": "No file selected"})
    
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Preprocess the image
        image = load_img(filepath, target_size=IMAGE_SIZE)
        image_array = img_to_array(image)
        image_array = image_array / 255.0  # Normalize if needed
        image_array = image_array.reshape(1, *IMAGE_SIZE, 3)

        # Make prediction
        predictions = model.predict(image_array)
        predicted_class = predictions.argmax(axis=-1)[0]  # Assuming a multi-class model

        # Remove the uploaded file
        os.remove(filepath)

        # Send JSON response
        return ({'prediction': f"YOUR RESULT: DIABETIC RETINOPATHY - {categories[int(predicted_class)]}"})
    
    return ({"error": "File processing failed"})

if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
