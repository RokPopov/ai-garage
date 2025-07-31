import logging
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from ..schemas import ProcessingState
from ..services.document_processor import DocumentProcessor
from ..services.extraction_service import ExtractionService
from ..services.pdf_generator import PDFGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessingWorkflow:
    """LangGraph workflow for processing legal documents end-to-end."""
    
    def __init__(self, openai_api_key: str | None = None):
        """
        Initialize the document processing workflow.
        
        Args:
            openai_api_key: OpenAI API key for extraction service
        """
        self.document_processor = DocumentProcessor()
        self.extraction_service = ExtractionService(api_key=openai_api_key)
        self.pdf_generator = PDFGenerator()
        self.memory = MemorySaver()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with nodes and edges."""
        workflow = StateGraph(ProcessingState)
        
        # Graph nodes
        workflow.add_node("validate_document", self._validate_document_node)
        workflow.add_node("process_document", self._process_document_node)
        workflow.add_node("extract_data", self._extract_data_node)
        workflow.add_node("generate_pdf", self._generate_pdf_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Graph edges
        workflow.add_edge(START, "validate_document")
        workflow.add_conditional_edges(
            "validate_document",
            self._should_continue_after_validation,
            {
                "continue": "process_document",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "process_document",
            self._should_continue_after_processing,
            {
                "continue": "extract_data",
                "error": "handle_error"
            }
        )
        workflow.add_conditional_edges(
            "extract_data",
            self._should_continue_after_extraction,
            {
                "continue": "generate_pdf",
                "error": "handle_error"
            }
        )
        workflow.add_edge("generate_pdf", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    def _validate_document_node(self, state: ProcessingState) -> ProcessingState:
        """Validate the uploaded document."""
        logger.info(f"Validating document: {state.file_path}")
        
        try:
            state.update_status("processing", "validate_document")
            
            if not self.document_processor.validate_file_format(state.file_path):
                state.error_message = f"Unsupported file format: {state.file_path}"
                state.update_status("failed", "validate_document")
                return state
            
            state.processing_metadata["validation"] = {
                "file_exists": True,
                "format_supported": True,
                "validated_at": "validate_document"
            }
            
            logger.info(f"Document validation successful: {state.file_path}")
            return state
            
        except Exception as e:
            logger.error(f"Document validation failed: {e}")
            state.error_message = f"Validation error: {str(e)}"
            state.update_status("failed", "validate_document")
            return state
    
    def _process_document_node(self, state: ProcessingState) -> ProcessingState:
        """Process the document and extract text using Docling."""
        logger.info(f"Processing document: {state.file_path}")
        
        try:
            state.update_status("processing", "process_document")
            
            result = self.document_processor.process_document(
                state.file_path, 
                state.document_type
            )
            
            if not result["success"]:
                state.error_message = f"Document processing failed: {result.get('error', 'Unknown error')}"
                state.update_status("failed", "process_document")
                return state
            
            state.extracted_text = result["extracted_text"]
            state.processing_metadata["document_processing"] = {
                "page_count": result.get("page_count", 1),
                "format": result.get("metadata", {}).get("format", "unknown"),
                "tables_found": result.get("metadata", {}).get("tables_found", 0),
                "processing_node": "process_document"
            }
            
            logger.info(f"Document processing successful: {state.file_path}")
            return state
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            state.error_message = f"Processing error: {str(e)}"
            state.update_status("failed", "process_document")
            return state
    
    def _extract_data_node(self, state: ProcessingState) -> ProcessingState:
        """Extract structured data using OpenAI and Instructor."""
        logger.info(f"Extracting structured data from {state.document_type}")
        
        try:
            state.update_status("processing", "extract_data")
            
            result = self.extraction_service.extract_from_document(
                state.extracted_text,
                state.document_type
            )
            
            if not result["success"]:
                state.error_message = f"Data extraction failed: {result.get('details', 'Unknown error')}"
                state.update_status("failed", "extract_data")
                return state
            
            state.structured_data = result["data"]
            state.processing_metadata["extraction"] = {
                "model_used": result.get("model_used", "unknown"),
                "extraction_successful": True,
                "extraction_node": "extract_data"
            }
            
            logger.info(f"Data extraction successful for {state.document_type}")
            return state
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            state.error_message = f"Extraction error: {str(e)}"
            state.update_status("failed", "extract_data")
            return state
    
    def _generate_pdf_node(self, state: ProcessingState) -> ProcessingState:
        """Generate PDF report from extracted data."""
        logger.info(f"Generating PDF for job: {state.job_id}")
        
        try:
            state.update_status("processing", "generate_pdf")
            
            if not state.structured_data:
                state.error_message = "No structured data available for PDF generation"
                state.update_status("failed", "generate_pdf")
                return state
            
            pdf_path = self.pdf_generator.generate_pdf(
                document_data=state.structured_data,
                document_type=state.document_type,
                job_id=state.job_id
            )
            
            state.pdf_path = pdf_path
            
            state.processing_metadata["pdf_generation"] = {
                "pdf_generated": True,
                "pdf_path": state.pdf_path,
                "generation_node": "generate_pdf"
            }
            
            state.update_status("completed", "generate_pdf")
            logger.info(f"PDF generation successful: {state.pdf_path}")
            return state
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            state.error_message = f"PDF generation error: {str(e)}"
            state.update_status("failed", "generate_pdf")
            return state
    
    def _handle_error_node(self, state: ProcessingState) -> ProcessingState:
        """Handle errors and determine if retry is possible."""
        logger.error(f"Handling error for job {state.job_id}: {state.error_message}")
        
        max_retries = 3
        if state.retry_count < max_retries:
            state.retry_count += 1
            logger.info(f"Retrying job {state.job_id} (attempt {state.retry_count})")
            
            state.update_status("pending", "retry")
            
        state.update_status("failed", "handle_error")
        
        state.processing_metadata["error_handling"] = {
            "final_error": state.error_message,
            "retry_count": state.retry_count,
            "error_node": "handle_error"
        }
        
        return state
    
    def _should_continue_after_validation(self, state: ProcessingState) -> Literal["continue", "error"]:
        """Determine next step after document validation."""
        return "continue" if state.processing_status != "failed" else "error"
    
    def _should_continue_after_processing(self, state: ProcessingState) -> Literal["continue", "error"]:
        """Determine next step after document processing."""
        return "continue" if state.processing_status != "failed" else "error"
    
    def _should_continue_after_extraction(self, state: ProcessingState) -> Literal["continue", "error"]:
        """Determine next step after data extraction."""
        return "continue" if state.processing_status != "failed" else "error"
    
    def process_document(self, initial_state: ProcessingState) -> ProcessingState:
        """
        Process a document through the complete workflow.
        
        Args:
            initial_state: Initial processing state
            
        Returns:
            Final processing state
        """
        logger.info(f"Starting document processing workflow for job: {initial_state.job_id}")
        
        try:
            thread_id = f"thread_{initial_state.job_id}"
            
            result = self.workflow.invoke(
                initial_state.model_dump(),
                {"configurable": {"thread_id": thread_id}}
            )
            
            final_state = ProcessingState(**result)
            
            logger.info(f"Workflow completed for job: {initial_state.job_id} with status: {final_state.processing_status}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed for job {initial_state.job_id}: {e}")
            initial_state.error_message = f"Workflow error: {str(e)}"
            initial_state.update_status("failed", "workflow_error")
            return initial_state
    
    def get_workflow_status(self, job_id: str) -> Dict[str, Any]:
        """Get the current status of a workflow job."""
        thread_id = f"thread_{job_id}"
        
        try:
            state = self.workflow.get_state({"configurable": {"thread_id": thread_id}})
            
            if state and state.values:
                return {
                    "job_id": job_id,
                    "status": state.values.get("processing_status", "unknown"),
                    "current_node": state.values.get("current_node"),
                    "metadata": state.values.get("processing_metadata", {})
                }
            else:
                return {
                    "job_id": job_id,
                    "status": "not_found",
                    "error": "Job not found in workflow state"
                }
                
        except Exception as e:
            logger.error(f"Error getting workflow status for job {job_id}: {e}")
            return {
                "job_id": job_id,
                "status": "error",
                "error": str(e)
            }


def create_workflow(openai_api_key: str | None = None) -> DocumentProcessingWorkflow:
    """
    Create a new document processing workflow.
    
    Args:
        openai_api_key: OpenAI API key
        
    Returns:
        Configured workflow instance
    """
    return DocumentProcessingWorkflow(openai_api_key=openai_api_key)
