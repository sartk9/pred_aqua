
from PIL import Image
from ultralytics import YOLO
import os
import pandas as pd
from datetime import datetime
from couchbase.cluster import Cluster, ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator




# Couchbase connection settings
cluster = Cluster('couchbase://localhost', ClusterOptions(PasswordAuthenticator('sartk', 'couchbasesartk9')))
bucket = cluster.bucket('classify')
collection = bucket.default_collection()






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
    
    
   
   
   



    

# Function to fetch documents as DataFrame
def fetch_documents_as_dataframe(start_date=None, end_date=None):
    try:
        query = f"SELECT * FROM classify"
        result = cluster.query(query, QueryOptions(adhoc=True))
        documents = []
        
        for row in result.rows():
            doc = row['classify']
            metadata = doc['metadata']
            individual_data = doc['individual_data']
            avg_all = doc['avg_all']
            
            # Filtering based on selected start and end dates
            if start_date and end_date:
                if start_date <= timestamp_date <= end_date:
                    pass
                else:
                    continue

            row_data = {
                 'id': metadata['id'],
        'image_path1': individual_data['img1']['image_path'],
        'image_path2': individual_data['img2']['image_path'],
        'image_path3': individual_data['img3']['image_path'],
        'image_path4': individual_data['img4']['image_path'],
        'image_path5': individual_data['img5']['image_path'],
        'lettuce1': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img1']['lettuce'].items()]),
        'lettuce2': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img2']['lettuce'].items()]),
        'lettuce3': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img3']['lettuce'].items()]),
        'lettuce4': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img4']['lettuce'].items()]),
        'lettuce5': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img5']['lettuce'].items()]),
        'disease1': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img1']['disease'].items()]),
        'disease2': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img2']['disease'].items()]),
        'disease3': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img3']['disease'].items()]),
        'disease4': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img4']['disease'].items()]),
        'disease5': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img5']['disease'].items()]),
        'pest1': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img1']['pest'].items()]),
        'pest2': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img2']['pest'].items()]),
        'pest3': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img3']['pest'].items()]),
        'pest4': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img4']['pest'].items()]),
        'pest5': "<br>".join([f"• {item}: {value}" for item, value in individual_data['img5']['pest'].items()]),
        'average_percentage_lettuce': "<br>".join([f"• {item}: {value}" for item, value in avg_all['average_percentage_lettuce'].items()]),
        'average_percentage_disease': "<br>".join([f"• {item}: {value}" for item, value in avg_all['average_percentage_disease'].items()]),
        'average_percentage_pest': "<br>".join([f"• {item}: {value}" for item, value in avg_all['average_percentage_pest'].items()]),
        'timestamp': doc['timestamp'],
        'create_dt': doc['create_dt'],
        'create_by': doc['create_by'],
        'update_dt': doc['update_dt'],
        'update_by': doc['update_by'],
        'affected_dt': doc['affected_dt']
            }
            
            documents.append(row_data)
        
        df = pd.DataFrame(documents)
        
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    
    
    
    
    
    
    
    
    

