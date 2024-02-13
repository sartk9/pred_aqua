from ultralytics import YOLO

# Initialize YOLO with the yolov8n-cls.pt model
model = YOLO('yolov8n-cls.pt')

# Specify the path where you want to save the trained weights file
weights_path = '/home/sarthak/Downloads/trained_weights.pth'

# Train the model
results = model.train(data='/home/sarthak/Downloads/Disease', epochs=10, imgsz=64)

# Save the trained weights
model.save(weights_path)

