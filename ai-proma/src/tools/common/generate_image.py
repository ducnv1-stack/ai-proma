import os
import uuid
import vertexai
from vertexai.vision_models import ImageGenerationModel
from google.cloud import storage
from google.adk.tools import FunctionTool

def _upload_to_gcs(local_file_path: str, file_name: str) -> str:
    try:
        client = storage.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT"))
        bucket = client.bucket(os.getenv("GCS_BUCKET_NAME"))
        blob_name = f"generated_images/{file_name}"
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_file_path)

        blob.make_public()
        public_url = blob.public_url

        if os.path.exists(local_file_path):
            os.remove(local_file_path)

        return public_url
    except Exception as e:
        return None


def generate_image(prompt: str) -> str:
    if not os.getenv("GOOGLE_CLOUD_PROJECT"):
        return "Error: GOOGLE_CLOUD_PROJECT not configured."

    if not os.getenv("GCS_BUCKET_NAME"):
        return "Error: GCS_BUCKET_NAME not configured."
        
    try:
        vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"))
        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        
        response = model.generate_images(prompt=prompt, number_of_images=1)
        generated_image = response.images[0]

        output_dir = "generated_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_name = f"{uuid.uuid4()}.png"
        local_file_path = os.path.abspath(os.path.join(output_dir, file_name))
        generated_image.save(location=local_file_path, include_generation_parameters=False)
        
        public_url = _upload_to_gcs(local_file_path, file_name)

        if public_url:
            return f"Image generated successfully! Public URL: {public_url}"
        else:
            return "Error: Image generated but could not upload to Cloud Storage."

    except Exception as e:
        return f"Error generating image: {e}"
    
generate_image_tool = FunctionTool(func=generate_image)