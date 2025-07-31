"""
Document processing service using Docling for extracting text from various document formats.
Handles employment contracts, payslips, and other legal documents.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Literal
from docling.document_converter import DocumentConverter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Service for processing legal documents using Docling."""
    
    def __init__(self):
        """Initialize the document processor with Docling converter."""
        self.converter = DocumentConverter()
        
    def process_document(
        self, 
        file_path: str | Path, 
        document_type: Literal["employment_contract", "payslip"]
    ) -> Dict[str, Any]:
        """
        Process a document and extract structured text.
        
        Args:
            file_path: Path to the document file
            document_type: Type of document being processed
            
        Returns:
            Dictionary containing processed document data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")
            
        logger.info(f"Processing {document_type} document: {file_path}")
        
        try:
            result = self.converter.convert(str(file_path))
            markdown_content = result.document.export_to_markdown()
            metadata = self._extract_metadata(result, document_type)
            cleaned_text = self._clean_text(markdown_content, document_type)
            
            return {
                "success": True,
                "document_type": document_type,
                "file_path": str(file_path),
                "extracted_text": cleaned_text,
                "raw_markdown": markdown_content,
                "metadata": metadata,
                "page_count": len(result.document.pages) if hasattr(result.document, 'pages') else 1
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "document_type": document_type,
                "file_path": str(file_path)
            }
    
    def _extract_metadata(self, result: Any, document_type: str) -> Dict[str, Any]:
        """Extract metadata from the processed document."""
        metadata = {
            "document_type": document_type,
            "processing_timestamp": None,
            "format": None,
            "tables_found": 0,
            "images_found": 0
        }
        
        try:
            if hasattr(result.document, 'origin'):
                metadata["format"] = result.document.origin.filename.split('.')[-1].lower()
            
            if hasattr(result.document, 'tables'):
                metadata["tables_found"] = len(result.document.tables)
            
            if hasattr(result.document, 'pictures'):
                metadata["images_found"] = len(result.document.pictures)
                
        except Exception as e:
            logger.warning(f"Could not extract complete metadata: {e}")
        
        return metadata
    
    def _clean_text(self, text: str, document_type: str) -> str:
        """Clean and preprocess extracted text based on document type."""
        if not text:
            return ""
        
        cleaned = text.strip()
        
        import re
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        if document_type == "employment_contract":
            cleaned = self._clean_contract_text(cleaned)
        elif document_type == "payslip":
            cleaned = self._clean_payslip_text(cleaned)
        
        return cleaned
    
    def _clean_contract_text(self, text: str) -> str:
        """Specific cleaning for employment contracts."""
        import re
        
        text = re.sub(r'Page \d+ of \d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'€\s*', '€', text)
        
        return text.strip()
    
    def _clean_payslip_text(self, text: str) -> str:
        """Specific cleaning for payslips."""
        import re
        
        text = re.sub(r'Payslip.*?Period:', 'Period:', text, flags=re.IGNORECASE)
        text = re.sub(r'€\s*(\d)', r'€\1', text)
        text = re.sub(r'\|+', '|', text)
        
        return text.strip()
    
    def get_supported_formats(self) -> list[str]:
        """Get list of supported document formats."""
        return [
            "pdf", "docx", "pptx", "xlsx", 
            "html", "png", "jpg", "jpeg", 
            "tiff", "bmp"
        ]
    
    def validate_file_format(self, file_path: str | Path) -> bool:
        """Validate if the file format is supported."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower().lstrip('.')
        return extension in self.get_supported_formats()


def process_document(
    file_path: str | Path, 
    document_type: Literal["employment_contract", "payslip"]
) -> Dict[str, Any]:
    """
    Convenience function to process a document.
    
    Args:
        file_path: Path to the document
        document_type: Type of document
        
    Returns:
        Processing result dictionary
    """
    processor = DocumentProcessor()
    return processor.process_document(file_path, document_type)
