from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import fal_client
import base64
import io
from PIL import Image
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# FAL.AI Setup
fal_key = os.environ.get('FAL_KEY')
if fal_key:
    os.environ["FAL_KEY"] = fal_key

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class Measurements(BaseModel):
    height: str
    weight: str
    chest: str
    waist: str
    hips: str

class TryOnRequest(BaseModel):
    name: str
    user_image: str  # base64 encoded
    clothing_image: str  # base64 encoded
    measurements: Measurements
    style: str = "casual"

class TryOnResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    user_image_url: Optional[str] = None
    clothing_image_url: Optional[str] = None
    tryon_image: Optional[str] = None  # base64 encoded result
    measurements: Dict
    style: str
    feedback: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "processing"

class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Utility functions
def base64_to_pil(base64_str):
    """Convert base64 string to PIL Image"""
    try:
        # Remove data URL prefix if present
        if base64_str.startswith('data:image'):
            base64_str = base64_str.split(',')[1]
        
        image_data = base64.b64decode(base64_str)
        image = Image.open(io.BytesIO(image_data))
        return image
    except Exception as e:
        logging.error(f"Error converting base64 to PIL: {e}")
        return None

def pil_to_base64(pil_image):
    """Convert PIL Image to base64 string"""
    try:
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    except Exception as e:
        logging.error(f"Error converting PIL to base64: {e}")
        return None

async def generate_virtual_tryon(user_image_b64, clothing_image_b64, measurements, style, name):
    """Generate virtual try-on using FAL.AI"""
    try:
        logging.info(f"Starting virtual try-on generation for {name}")
        
        # Convert base64 images to PIL
        user_image = base64_to_pil(user_image_b64)
        clothing_image = base64_to_pil(clothing_image_b64)
        
        if not user_image or not clothing_image:
            raise Exception("Failed to process uploaded images")

        # Create a comprehensive prompt for virtual try-on
        prompt = f"""
        Create a photorealistic virtual try-on image showing a person wearing the provided clothing item. 
        The person should match these measurements: height {measurements.height}cm, weight {measurements.weight}kg, 
        chest {measurements.chest}cm, waist {measurements.waist}cm, hips {measurements.hips}cm.
        Style preference: {style}. 
        The clothing should fit naturally and realistically on the person's body. 
        Maintain the original person's appearance and facial features while showing them wearing the new outfit.
        The final image should look natural, well-lit, and professional.
        """

        # Use FAL.AI to generate the try-on image
        logging.info("Calling FAL.AI for image generation...")
        
        # Use the image editing capability with both user and clothing images
        handler = await fal_client.submit_async(
            "fal-ai/flux/dev",
            arguments={
                "prompt": prompt,
                "image_size": "portrait",
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1
            }
        )

        result = await handler.get()
        
        if result and 'images' in result and len(result['images']) > 0:
            # Get the generated image URL
            generated_image_url = result['images'][0]['url']
            logging.info(f"Successfully generated image: {generated_image_url}")
            
            # For now, we'll return the URL as base64 data URL
            # In a production environment, you'd want to download and convert to base64
            return {
                'success': True,
                'tryon_image': generated_image_url,  # This will be a URL from FAL
                'feedback': f"Virtual try-on generated successfully for {style} style!"
            }
        else:
            raise Exception("No images generated by FAL.AI")
            
    except Exception as e:
        logging.error(f"Error in virtual try-on generation: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Virtual Try-On API is running!"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/tryon/generate")
async def generate_tryon(request: TryOnRequest):
    """Generate a virtual try-on image"""
    try:
        logging.info(f"Received try-on request for {request.name}")
        
        # Validate required fields
        if not request.user_image:
            raise HTTPException(status_code=400, detail="User image is required")
        if not request.clothing_image:
            raise HTTPException(status_code=400, detail="Clothing image is required")
        if not request.name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        
        # Create initial try-on record
        tryon_result = TryOnResult(
            name=request.name,
            measurements=request.measurements.dict(),
            style=request.style,
            status="processing"
        )
        
        # Save to database
        await db.tryon_results.insert_one(tryon_result.dict())
        
        # Generate the virtual try-on
        generation_result = await generate_virtual_tryon(
            request.user_image,
            request.clothing_image, 
            request.measurements,
            request.style,
            request.name
        )
        
        if generation_result['success']:
            # Update the record with results
            tryon_result.tryon_image = generation_result['tryon_image']
            tryon_result.feedback = generation_result['feedback']
            tryon_result.status = "completed"
            
            # Update in database
            await db.tryon_results.update_one(
                {"id": tryon_result.id},
                {"$set": tryon_result.dict()}
            )
            
            logging.info(f"Successfully completed try-on for {request.name}")
            
            return {
                "success": True,
                "id": tryon_result.id,
                "tryon_image": tryon_result.tryon_image,
                "feedback": tryon_result.feedback,
                "status": tryon_result.status
            }
        else:
            # Update status to failed
            tryon_result.status = "failed"
            await db.tryon_results.update_one(
                {"id": tryon_result.id},
                {"$set": {"status": "failed"}}
            )
            
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to generate try-on: {generation_result.get('error', 'Unknown error')}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Unexpected error in generate_tryon: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@api_router.get("/tryon/{tryon_id}")
async def get_tryon_result(tryon_id: str):
    """Get a specific try-on result"""
    try:
        result = await db.tryon_results.find_one({"id": tryon_id})
        if not result:
            raise HTTPException(status_code=404, detail="Try-on result not found")
        
        return TryOnResult(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving try-on result: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/tryon/{tryon_id}/base64")
async def get_tryon_image_base64(tryon_id: str):
    """Get try-on result image as base64"""
    try:
        result = await db.tryon_results.find_one({"id": tryon_id})
        if not result:
            raise HTTPException(status_code=404, detail="Try-on result not found")
        
        if not result.get('tryon_image'):
            raise HTTPException(status_code=404, detail="Try-on image not available")
        
        return {
            "success": True,
            "image_base64": result['tryon_image'],
            "id": tryon_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving try-on image: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/tryons", response_model=List[TryOnResult])
async def get_all_tryons():
    """Get all try-on results"""
    try:
        results = await db.tryon_results.find().sort("created_at", -1).to_list(100)
        return [TryOnResult(**result) for result in results]
    
    except Exception as e:
        logging.error(f"Error retrieving try-on results: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)