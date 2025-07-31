import logging
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from .schemas import ProcessingState
from .workflows.processing_workflow import DocumentProcessingWorkflow

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

workflow_instance: DocumentProcessingWorkflow = None
job_storage: Dict[str, ProcessingState] = {}
thread_pool = ThreadPoolExecutor(max_workers=4)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}


class UploadResponse(BaseModel):
    """Response model for file upload."""
    job_id: str = Field(..., description="Unique job identifier")
    message: str = Field(..., description="Upload status message")
    file_path: str = Field(..., description="Path to uploaded file")


class ProcessingStatusResponse(BaseModel):
    """Response model for processing status."""
    job_id: str = Field(..., description="Job identifier")
    status: str = Field(..., description="Current processing status")
    current_node: str | None = Field(None, description="Current workflow node")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    error_message: str | None = Field(None, description="Error message if failed")


class ProcessingResultResponse(BaseModel):
    """Response model for processing results."""
    job_id: str = Field(..., description="Job identifier")
    success: bool = Field(..., description="Processing success status")
    document_type: str = Field(..., description="Type of document processed")
    extracted_data: Dict[str, Any] | None = Field(None, description="Extracted structured data")
    pdf_path: str | None = Field(None, description="Path to generated PDF")
    error_message: str | None = Field(None, description="Error message if failed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global workflow_instance
    
    logger.info("Starting FastAPI application...")
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        raise RuntimeError("OPENAI_API_KEY environment variable is required")
    
    workflow_instance = DocumentProcessingWorkflow(openai_api_key=openai_api_key)
    logger.info("Document processing workflow initialized")
    
    yield
    
    logger.info("Shutting down FastAPI application...")
    thread_pool.shutdown(wait=True)


app = FastAPI(
    title="Legal Document Intake API",
    description="API for processing employment contracts and payslips",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer(auto_error=False)

async def get_current_user(token: str = Depends(security)):
    """Get current user from token (placeholder for future auth)."""
    # TODO: Implement proper authentication
    return {"user_id": "demo_user"}


def validate_file_upload(file: UploadFile) -> None:
    """Validate uploaded file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_extension} not supported. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    if hasattr(file, 'size') and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
        )


async def save_uploaded_file(file: UploadFile, job_id: str) -> Path:
    """Save uploaded file to disk."""
    file_extension = Path(file.filename).suffix.lower()
    file_path = UPLOAD_DIR / f"{job_id}{file_extension}"
    
    try:
        content = await file.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"File saved: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        raise HTTPException(status_code=500, detail="Error saving file")


def process_document_background(job_id: str, file_path: str, document_type: str):
    """Background task for processing documents."""
    try:
        logger.info(f"Starting background processing for job: {job_id}")
        
        initial_state = ProcessingState(
            job_id=job_id,
            document_type=document_type,
            file_path=file_path
        )
        
        final_state = workflow_instance.process_document(initial_state)
        job_storage[job_id] = final_state
        
        logger.info(f"Background processing completed for job: {job_id}")
        
    except Exception as e:
        logger.error(f"Background processing failed for job {job_id}: {e}")
        
        error_state = ProcessingState(
            job_id=job_id,
            document_type=document_type,
            file_path=file_path,
            processing_status="failed",
            error_message=str(e)
        )
        job_storage[job_id] = error_state


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Legal Document Intake API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    job_counts = {
        "pending": 0,
        "processing": 0,
        "completed": 0,
        "failed": 0
    }
    
    for job_state in job_storage.values():
        status = job_state.processing_status
        if status in job_counts:
            job_counts[status] += 1
    
    return {
        "status": "healthy",
        "workflow_initialized": workflow_instance is not None,
        "total_jobs": len(job_storage),
        "jobs_by_status": job_counts,
        "active_jobs": job_counts["pending"] + job_counts["processing"]
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload a document for processing.
    
    Args:
        file: Document file (PDF, DOCX, or image)
        document_type: Type of document (employment_contract or payslip)
        background_tasks: FastAPI background tasks
        current_user: Current user (from authentication)
        
    Returns:
        Upload response with job ID
    """
    if document_type not in ["employment_contract", "payslip"]:
        raise HTTPException(
            status_code=400,
            detail="document_type must be either 'employment_contract' or 'payslip'"
        )
    
    validate_file_upload(file)
    
    job_id = str(uuid.uuid4())
    
    try:
        file_path = await save_uploaded_file(file, job_id)
        
        background_tasks.add_task(
            process_document_background,
            job_id,
            str(file_path),
            document_type
        )
        
        initial_state = ProcessingState(
            job_id=job_id,
            document_type=document_type,
            file_path=str(file_path),
            processing_status="pending"
        )
        job_storage[job_id] = initial_state
        
        logger.info(f"Document uploaded and processing started: {job_id}")
        
        return UploadResponse(
            job_id=job_id,
            message="Document uploaded successfully. Processing started.",
            file_path=str(file_path)
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")


@app.get("/status/{job_id}", response_model=ProcessingStatusResponse)
async def get_processing_status(job_id: str):
    """
    Get processing status for a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Current processing status
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    state = job_storage[job_id]
    
    return ProcessingStatusResponse(
        job_id=job_id,
        status=state.processing_status,
        current_node=state.current_node,
        metadata=state.processing_metadata,
        error_message=state.error_message
    )


@app.get("/result/{job_id}", response_model=ProcessingResultResponse)
async def get_processing_result(job_id: str):
    """
    Get processing results for a completed job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        Processing results including extracted data
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    state = job_storage[job_id]
    
    if state.processing_status == "processing":
        raise HTTPException(status_code=202, detail="Processing still in progress")
    
    return ProcessingResultResponse(
        job_id=job_id,
        success=state.processing_status == "completed",
        document_type=state.document_type,
        extracted_data=state.structured_data,
        pdf_path=state.pdf_path,
        error_message=state.error_message
    )


@app.get("/download/{job_id}")
async def download_pdf(job_id: str):
    """
    Download generated PDF for a job.
    
    Args:
        job_id: Job identifier
        
    Returns:
        PDF file response
    """
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    state = job_storage[job_id]
    
    if state.processing_status != "completed":
        raise HTTPException(status_code=400, detail="Processing not completed")
    
    if not state.pdf_path or not Path(state.pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        path=state.pdf_path,
        media_type="application/pdf",
        filename=f"{job_id}.pdf"
    )


@app.get("/jobs", response_model=List[ProcessingStatusResponse])
async def list_jobs():
    """List all jobs in the system."""
    return [
        ProcessingStatusResponse(
            job_id=job_id,
            status=state.processing_status,
            current_node=state.current_node,
            metadata=state.processing_metadata,
            error_message=state.error_message
        )
        for job_id, state in job_storage.items()
    ]


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its associated files."""
    if job_id not in job_storage:
        raise HTTPException(status_code=404, detail="Job not found")
    
    state = job_storage[job_id]
    
    try:
        if state.file_path and Path(state.file_path).exists():
            Path(state.file_path).unlink()
        
        if state.pdf_path and Path(state.pdf_path).exists():
            Path(state.pdf_path).unlink()
    except Exception as e:
        logger.warning(f"Error deleting files for job {job_id}: {e}")
    
    del job_storage[job_id]
    
    return {"message": f"Job {job_id} deleted successfully"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "status_code": 500}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
