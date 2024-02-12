from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from database import process_data
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import uuid
from datetime import datetime

app = FastAPI()

# Connect to Couchbase
authenticator = PasswordAuthenticator('sartk', 'couchbasesartk9')
options = ClusterOptions(authenticator)
cluster = Cluster('couchbase://localhost', options)
bucket = cluster.bucket('classify')
collection = bucket.default_collection()

@app.post("/classify")
async def classify(data: dict):
    try:
        # Check if exactly 5 image paths are provided
        if "image_paths" not in data or len(data["image_paths"]) != 5:
            raise HTTPException(status_code=400, detail="Exactly 5 image paths are required.")

        # Ensure create_by is provided
        create_by = data.get("create_by")
        if not create_by:
            raise HTTPException(status_code=400, detail="create_by field is required.")

        # Process the data
        combined_data = process_data(data, create_by=create_by)

        # Generate a unique document ID by combining create_by and timestamp
        timestamp = datetime.now().isoformat()  # Get the current timestamp in ISO format
        doc_id = f"{create_by}_{timestamp}"  # Combine create_by and timestamp for document ID

        # Store the combined data in Couchbase using the generated ID
        collection.upsert(doc_id, combined_data)

        # Return a success response with the document ID
        return JSONResponse(content={"status": "success", "message": "Data processed and stored successfully.", "document_id": doc_id})
    except Exception as e:
        # Return an error response if an exception occurs
        return JSONResponse(content={"status": "error", "message": str(e)})

