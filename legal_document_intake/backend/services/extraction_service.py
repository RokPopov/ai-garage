import logging
import os
from typing import Dict, Any, Type, TypeVar
import instructor
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

from ..schemas import EmploymentContract, PayslipData

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


class ExtractionService:
    """Service for extracting structured data from legal documents using OpenAI + Instructor."""
    
    def __init__(self, api_key: str | None = None):
        """
        Initialize the extraction service.
        
        Args:
            api_key: OpenAI API key (if None, will use OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        openai_client = OpenAI(api_key=self.api_key)
        
        self.client = instructor.from_openai(openai_client)
        
        self.prompts = {
            "employment_contract": self._get_contract_extraction_prompt(),
            "payslip": self._get_payslip_extraction_prompt()
        }
    
    def extract_employment_contract(self, document_text: str) -> Dict[str, Any]:
        """
        Extract structured data from employment contract text.
        
        Args:
            document_text: Raw text extracted from the employment contract
            
        Returns:
            Dictionary containing extraction results
        """
        return self._extract_structured_data(
            document_text=document_text,
            response_model=EmploymentContract,
            document_type="employment_contract"
        )
    
    def extract_payslip_data(self, document_text: str) -> Dict[str, Any]:
        """
        Extract structured data from payslip text.
        
        Args:
            document_text: Raw text extracted from the payslip
            
        Returns:
            Dictionary containing extraction results
        """
        return self._extract_structured_data(
            document_text=document_text,
            response_model=PayslipData,
            document_type="payslip"
        )
    
    def _extract_structured_data(
        self, 
        document_text: str, 
        response_model: Type[T], 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Generic method for extracting structured data using Instructor.
        
        Args:
            document_text: Raw document text
            response_model: Pydantic model class
            document_type: Type of document being processed
            
        Returns:
            Dictionary containing extraction results
        """
        try:
            logger.info(f"Extracting {document_type} data using {response_model.__name__}")
            system_prompt = self.prompts.get(document_type, "")

            extracted_data = self.client.chat.completions.create(
                model="gpt-4.1",
                response_model=response_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Extract structured data from the following {document_type}:\n\n{document_text}"
                    }
                ],
                temperature=0.1,
                max_retries=3,
            )
            
            return {
                "success": True,
                "data": extracted_data.model_dump(),
                "model_used": response_model.__name__,
                "document_type": document_type
            }
            
        except ValidationError as e:
            logger.error(f"Validation error during {document_type} extraction: {e}")
            return {
                "success": False,
                "error": "validation_error",
                "details": str(e),
                "document_type": document_type
            }
        
        except Exception as e:
            logger.error(f"Unexpected error during {document_type} extraction: {e}")
            return {
                "success": False,
                "error": "extraction_error",
                "details": str(e),
                "document_type": document_type
            }
    
    def _get_contract_extraction_prompt(self) -> str:
        """Get the system prompt for employment contract extraction."""
        return """
You are an expert legal document processor specializing in employment contracts.
Your task is to extract structured information from employment contract documents.

IMPORTANT INSTRUCTIONS:
1. Extract information exactly as it appears in the document
2. For dates, use YYYY-MM-DD format
3. For monetary amounts, extract numerical values only (no currency symbols)
4. If information is not found, leave the field empty or use appropriate default values
5. Pay special attention to:
   - Employee personal details (name, address, birth date)
   - Employment terms (start date, job title, contract type)
   - Compensation details (salary, allowances, benefits)
   - Working conditions (hours, probation period)
   - Employer information

SPECIFIC FIELD GUIDELINES:
- other_benefits: Extract ONLY actual employee benefits and perks, format as bullet points:
  * Health insurance contributions (amounts)
  * Company car, laptop, phone
  * Meal vouchers, gym membership
  * Training budget, professional development
  * Flexible working arrangements
  * Additional vacation days beyond standard
  
  FORMAT: Use bullet points (•) for each benefit, one per line
  EXAMPLE: 
  • Health insurance contribution €145 per month
  • Travel allowance for public transportation
  • Company laptop provided
  
DO NOT include in other_benefits:
- Standard legal provisions (confidentiality, non-compete clauses)
- Standard employment policies (sick leave, pension participation)
- Expense reimbursement policies
- Standard holiday entitlements
- Legal obligations or compliance requirements
- Background check procedures

Be precise and thorough in your extraction. If you're unsure about a value, it's better to leave it empty than to guess.
"""
    
    def _get_payslip_extraction_prompt(self) -> str:
        """Get the system prompt for payslip extraction."""
        return """
You are an expert payroll processor specializing in Dutch payslips.
Your task is to extract structured information from payslip documents.

IMPORTANT INSTRUCTIONS:
1. Extract information exactly as it appears in the document
2. For dates, use YYYY-MM-DD format
3. For monetary amounts, extract numerical values only (no currency symbols, no commas)
4. For percentages, extract as decimal numbers (e.g., 8.5 for 8.5%)
5. For boolean fields, determine true/false based on document content
6. Look for information in tables, sections, and labeled fields

FIELD MAPPING GUIDE:
- employee_name: Look for "Naam", "Employee Name", or similar
- employee_number: Look for "Employee no.", "Personeelsnummer", "Employee Number", "Nr"
- gross_salary_period: Look for "Salaris", "Period salary", "Bruto loon", "Gross Salary"
- net_salary_paid: Look for "Total net", "Payment", "Netto uitbetaling", "Net Pay"
- wage_tax_withheld: Look for "Loonheffing", "Wage tax", "Tax", in withholding/deduction sections
- social_security_wage_to_date: Look for "Total wage Ssl", "SV loon t/m", "Social Security YTD"
- fiscal_wage_to_date: Look for "Fiscal wage tax", "Fiscaal loon t/m", "Fiscal wage YTD"
- annual_gross_salary: Look for "Annual wage", "Jaarsalaris", "Annual Salary"
- zvw_employer_contribution: Look for "ZVW", "Aanv. WG bijdrage ZVW", "Health Insurance"
- holiday_allowance: Look for "Vakantiegeld", "Holiday Allowance", code "7100"
- work_days_this_period: Look for "Days worked", "Werkdagen", "Work Days"
- iban: Look for account numbers starting with "NL" (like "NL94INGB0799257958")
- payroll_period: Look for "Period" at the top, format like "4 - 0 - 2025"

CRITICAL DISTINCTIONS for Dutch payslips:
- "Total wage Ssl" = social_security_wage_to_date (NOT fiscal wage)
- "Fiscal wage tax" = fiscal_wage_to_date (NOT social security wage)
- These are two different fields with different values

Dutch payslip specific terms:
- ZVW = Zorgverzekeringswet (Health Insurance Act)
- WGA = Werkhervatting Gedeeltelijk Arbeidsgeschikten
- SV = Sociale Verzekering (Social Security)
- Loonheffing = Wage Tax
- Bruto = Gross
- Netto = Net

SPECIAL INSTRUCTIONS:
- Look carefully in tables for YTD (year-to-date) amounts
- Social security amounts are often in separate columns or sections  
- Some fields might be in different languages (Dutch/English)
- Focus on extracting accurate monetary amounts and employee identification info

Be precise and thorough in your extraction. If you're unsure about a value, it's better to leave it empty than to guess.
"""
    
    def extract_from_document(
        self, 
        document_text: str, 
        document_type: str
    ) -> Dict[str, Any]:
        """
        Extract structured data from any supported document type.
        
        Args:
            document_text: Raw document text
            document_type: Type of document ("employment_contract" or "payslip")
            
        Returns:
            Dictionary containing extraction results
        """
        if document_type == "employment_contract":
            return self.extract_employment_contract(document_text)
        elif document_type == "payslip":
            return self.extract_payslip_data(document_text)
        else:
            return {
                "success": False,
                "error": "unsupported_document_type",
                "details": f"Document type '{document_type}' is not supported",
                "supported_types": ["employment_contract", "payslip"]
            }
    
    def test_connection(self) -> bool:
        """Test the OpenAI API connection."""
        try:
            self.client.chat.completions.create(
                model="gpt-4.1",
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


def extract_employment_contract(document_text: str, api_key: str | None = None) -> Dict[str, Any]:
    """
    Convenience function to extract employment contract data.
    
    Args:
        document_text: Raw document text
        api_key: OpenAI API key (optional)
        
    Returns:
        Extraction results
    """
    service = ExtractionService(api_key=api_key)
    return service.extract_employment_contract(document_text)


def extract_payslip_data(document_text: str, api_key: str | None = None) -> Dict[str, Any]:
    """
    Convenience function to extract payslip data.
    
    Args:
        document_text: Raw document text
        api_key: OpenAI API key (optional)
        
    Returns:
        Extraction results
    """
    service = ExtractionService(api_key=api_key)
    return service.extract_payslip_data(document_text)
    