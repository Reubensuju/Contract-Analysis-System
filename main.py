from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.database import init_db, insert_document, get_document, extract_file_text
from src.document_analyzer import analyze_document
import uvicorn
import json
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Contract Analysis Server",
    description="AI-powered contract analysis system providing document processing, risk assessment, and compliance checking",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the React build directory
app.mount("/static", StaticFiles(directory="build/static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup"""
    await init_db()

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}

@app.post("/api/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    try:
        # Read the file content
        file_content = await file.read()
        
        # Insert into database
        doc_id = await insert_document(
            filename=file.filename,
            content_type=file.content_type,
            file_data=file_content
        )
        
        # Start document analysis in background
        await analyze_document(doc_id)
        
        return {
            "message": "PDF file successfully received and analysis started",
            "document_id": doc_id,
            "filename": file.filename,
            "content_type": file.content_type
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@app.get("/api/documents/{doc_id}")
async def get_document_info(doc_id: int):
    try:
        doc = await get_document(doc_id)
        if doc is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found"
            )
        
        # Parse JSON strings back to lists
        parties = json.loads(doc[8]) if doc[8] else []
        dates = json.loads(doc[9]) if doc[9] else []
        terms = json.loads(doc[10]) if doc[10] else []
        requirements = json.loads(doc[11]) if doc[11] else []
        
        return {
            "id": doc[0],
            "filename": doc[1],
            "content_type": doc[2],
            "file_size": doc[4],
            "upload_date": doc[5],
            "status": doc[6],
            "file_text": doc[7],
            "parties_involved": parties,
            "effective_dates": dates,
            "renewal_terms": terms,
            "compliance_requirements": requirements,
            "compliance": bool(doc[12]) if doc[12] is not None else None,
            "risk": doc[13],
            "renewal": doc[14],
            "contract_summary": doc[15],
            "potential_risks": doc[16]  # Return directly as string
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

# Custom Error Handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"error": "Not Found", "message": exc.detail}
    )

@app.exception_handler(400)
async def bad_request_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=400,
        content={"error": "Bad Request", "message": exc.detail}
    )

@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "message": "Something went wrong on our end."}
    )

# Serve index.html for all other routes to support React Router
@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
        
    return FileResponse(
        "build/index.html",
        media_type="text/html"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
