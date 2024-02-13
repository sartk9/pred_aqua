from collections import defaultdict
from PIL import Image
from ultralytics import YOLO
import os
import uuid
from datetime import datetime


model1 = YOLO("/home/sarthak/Downloads/runs/classify/train14/weights/best.pt")  # lettuce
model2 = YOLO("/home/sarthak/Downloads/runs/classify/train/weights/best.pt")  # disease
model3 = YOLO("/home/sarthak/Downloads/runs/classify/train13/weights/best.pt")  # pest

def get_top_predictions(results):
    names_dict = results[0].names
    probs = results[0].probs.data.tolist()
    indices = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:3]  # Get indices of top 3 probabilities
    return [(names_dict[i], probs[i]) for i in indices]

def predict_with_model(model, image_paths):
    all_predictions = []
    base_dir = "/home/sarthak/Downloads/graph/"  # Specify the base directory path
    for i, image_path in enumerate(image_paths, start=1):
        full_image_path = os.path.join(base_dir, image_path)  # Construct the full image path
        print("Full Image Path:", full_image_path)  # Print full image path

        if os.path.exists(full_image_path):  # Check if the file exists
            with Image.open(full_image_path) as img:
                img = img.resize((255, 255))
                results = model(img, show=True)  # Disable image display for prediction
                top_predictions = get_top_predictions(results)
                all_predictions.append(top_predictions)
        else:
            print(f"File not found1: {full_image_path}")  # Print a message if the file is not found

    return all_predictions

def process_data(data, create_dt=None, create_by=None, update_dt=None, update_by=None, affected_dt=None):
    # Ensure exactly 5 images are provided
    if "image_paths" not in data or len(data["image_paths"]) != 5:
        raise ValueError("Exactly 5 image paths are required.")

    individual_data = {}

    for i, image_path in enumerate(data["image_paths"], start=1):
        full_image_path = os.path.join("/home/sarthak/Downloads/graph/", image_path)
        lettuce_predictions = predict_with_model(model1, [image_path])
        disease_predictions = predict_with_model(model2, [image_path])
        pest_predictions = predict_with_model(model3, [image_path])

        individual_data[f"img{i}"] = {
            "image_path": full_image_path,
            "lettuce": {class_name: round(confidence * 100, 6) for class_name, confidence in lettuce_predictions[0]},
            "disease": {class_name: round(confidence * 100, 6) for class_name, confidence in disease_predictions[0]},
            "pest": {class_name: round(confidence * 100, 6) for class_name, confidence in pest_predictions[0]}
        }

    # Calculate average percentages
    avg_percentage_model1 = defaultdict(float)
    avg_percentage_model2 = defaultdict(float)
    avg_percentage_model3 = defaultdict(float)

    total_images = len(individual_data)

    for img_data in individual_data.values():
        for class_name, confidence in img_data["lettuce"].items():
            avg_percentage_model1[class_name] += confidence / total_images
        for class_name, confidence in img_data["disease"].items():
            avg_percentage_model2[class_name] += confidence / total_images
        for class_name, confidence in img_data["pest"].items():
            avg_percentage_model3[class_name] += confidence / total_images

    # Sort dictionaries in decreasing order of percentage
    avg_percentage_model1 = dict(sorted(avg_percentage_model1.items(), key=lambda item: item[1], reverse=True))
    avg_percentage_model2 = dict(sorted(avg_percentage_model2.items(), key=lambda item: item[1], reverse=True))
    avg_percentage_model3 = dict(sorted(avg_percentage_model3.items(), key=lambda item: item[1], reverse=True))

    # Get current timestamp
    timestamp = datetime.now().isoformat()

    # Generate id by combining create_by and timestamp
    id = f"{create_by}_{timestamp}"

    # Create the combined data structure
    combined_data = {
        "metadata": {
            "tab": "crop_mangmt_disease",
            "id": id
           
        },
        "create_dt": create_dt or "",
        "create_by": create_by or "",
        "update_dt": update_dt or "",
        "update_by": update_by or "",
        "affected_dt": affected_dt or "",
        "individual_data": individual_data,
        "avg_all": {
            "average_percentage_lettuce": avg_percentage_model1,
            "average_percentage_disease": avg_percentage_model2,
            "average_percentage_pest": avg_percentage_model3
        },
  "timestamp": timestamp
    }

    return combined_data
    
    
    
    
    
    
    
    
    
    
    
    
    

