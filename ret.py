from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from database import process_data,fetch_documents_as_dataframe
from couchbase.cluster import Cluster, ClusterOptions, QueryOptions
from couchbase.auth import PasswordAuthenticator
import pandas as pd
import os
from datetime import datetime




app = FastAPI()

# Couchbase connection settings
cluster = Cluster('couchbase://localhost', ClusterOptions(PasswordAuthenticator('sartk', 'couchbasesartk9')))
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

        # Add create_dt with the present date (date only, no time)
        combined_data['create_dt'] = datetime.now().strftime('%d-%m-%Y')  # Format the date as dd-mm-yyyy

        # Store the combined data in Couchbase using the generated ID
        collection.upsert(doc_id, combined_data)

        # Return a success response with the document ID
        return JSONResponse(content={"status": "success", "message": "Data processed and stored successfully.", "document_id": doc_id})
    except Exception as e:
        # Return an error response if an exception occurs
        return JSONResponse(content={"status": "error", "message": str(e)})












# Endpoint to display table with images
@app.get("/", response_class=HTMLResponse)
async def display_table(start_date: str = None, end_date: str = None):
    try:
        # HTML form for date selection
        date_form = """
        <form method="get">
            <label for="start_date">Start Date:</label>
            <input type="date" id="start_date" name="start_date"><br><br>
            <label for="end_date">End Date:</label>
            <input type="date" id="end_date" name="end_date"><br><br>
            <input type="submit" value="Filter">
        </form>
        """

        # Fetch documents as DataFrame
        df = fetch_documents_as_dataframe(start_date, end_date)

        if df.empty:
            return date_form + "<p>No results found within the selected date range.</p>"

        # Endpoint to serve images






@app.get("/images/{image_path:path}")
async def get_image(image_path: str):
            image_full_path = image_path  # Using full image path provided in the JSON
            if os.path.exists(image_full_path):
                return FileResponse(image_full_path)
            else:
                raise HTTPException(status_code=404, detail="Image not found")

        # Create a new column 'photos' to display images
        df['photo1'] = df.apply(lambda row: f'<img src="/images/{row["image_path1"]}" style="max-width:100px; max-height:100px;">', axis=1)
        df['photo2'] = df.apply(lambda row: f'<img src="/images/{row["image_path2"]}" style="max-width:100px; max-height:100px;">', axis=1)
        df['photo3'] = df.apply(lambda row: f'<img src="/images/{row["image_path3"]}" style="max-width:100px; max-height:100px;">', axis=1)
        df['photo4'] = df.apply(lambda row: f'<img src="/images/{row["image_path4"]}" style="max-width:100px; max-height:100px;">', axis=1)
        df['photo5'] = df.apply(lambda row: f'<img src="/images/{row["image_path5"]}" style="max-width:100px; max-height:100px;">', axis=1)

        # Concatenate image paths
        df['image_paths'] = df.apply(lambda row: '<br>'.join(row[f'image_path{i}'] for i in range(1, 6)), axis=1)

        # Concatenate lettuce predictions
        df['lettuce_predictions'] = df.apply(lambda row: '<br>'.join(str(row[f'lettuce{i}']) for i in range(1, 6)), axis=1)

        # Concatenate disease predictions
        df['disease_predictions'] = df.apply(lambda row: '<br>'.join(str(row[f'disease{i}']) for i in range(1, 6)), axis=1)

        # Concatenate pest predictions
        df['pest_predictions'] = df.apply(lambda row: '<br>'.join(str(row[f'pest{i}']) for i in range(1, 6)), axis=1)

        # Drop individual image path and prediction columns
        df.drop(columns=[f'image_path{i}' for i in range(1, 6)], inplace=True)
        df.drop(columns=[f'lettuce{i}' for i in range(1, 6)], inplace=True)
        df.drop(columns=[f'disease{i}' for i in range(1, 6)], inplace=True)
        df.drop(columns=[f'pest{i}' for i in range(1, 6)], inplace=True)

        # Render DataFrame as HTML table
        html_table = df.to_html(index=False, escape=False)
        html_table = html_table.replace('<th>', '<th style="text-align:center">')

        # Return HTML response with form and table
        
        return date_form + html_table

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

