import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50

# Load the ResNet50 model architecture from JSON file
with open("resnet50.json", "r") as json_file:
    loaded_model_json = json_file.read()

loaded_model = tf.keras.models.model_from_json(loaded_model_json)

# Load the model weights from H5 file
loaded_model.load_weights("resnet50.h5")
input_shape = (224, 224, 3)
# benign 0
# malignant 1

# Create a new model using the loaded model's input and output
model = ResNet50(
    input_tensor=loaded_model.input,
    weights=None,
    include_top=True,
    input_shape=input_shape,
    pooling="avg",
    classes=2,
)
