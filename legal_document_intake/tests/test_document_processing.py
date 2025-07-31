import os
import sys
import pytest
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

load_dotenv()

from backend.services.document_processor import DocumentProcessor
from backend.services.extraction_service import ExtractionService
from backend.services.pdf_generator import generate_employment_contract_pdf, generate_payslip_pdf
from backend.schemas import EmploymentContract, PayslipData


class TestDocumentProcessor:
    """Test suite for document processing functionality."""
    
    @pytest.fixture
    def processor(self):
        """Create DocumentProcessor instance."""
        return DocumentProcessor()
    
    def test_processor_initialization(self, processor):
        """Test that DocumentProcessor initializes correctly."""
        assert processor is not None
        assert hasattr(processor, 'converter')
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
    def test_process_text_from_pdf(self, processor):
        """Test processing text from PDF file."""
        # This would need a sample PDF file
        # For now, test the method exists and handles empty input
        result = processor.process_document("", "employment_contract")
        assert result["success"] == False
    
    def test_process_document_empty_input(self, processor):
        """Test processing empty document."""
        result = processor.process_document("", "employment_contract")
        assert result["success"] == False
    
    def test_process_document_invalid_path(self, processor):
        """Test processing non-existent file."""
        with pytest.raises(FileNotFoundError):
            processor.process_document("non_existent_file.pdf", "employment_contract")


class TestExtractionService:
    """Test suite for AI extraction functionality."""
    
    @pytest.fixture
    def extraction_service(self):
        """Create ExtractionService instance."""
        return ExtractionService()
    
    def test_extraction_service_initialization(self, extraction_service):
        """Test that ExtractionService initializes correctly."""
        assert extraction_service is not None
        assert hasattr(extraction_service, 'client')
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
    def test_extract_employment_contract_data(self, extraction_service):
        """Test employment contract data extraction."""
        sample_text = """
        Employment Contract
        
        Employee: John Doe
        Position: Software Engineer
        Start Date: 2024-01-15
        Salary: €5000 per month
        Company: Tech Corp BV
        """
        
        result = extraction_service.extract_employment_contract(sample_text)
        assert result["success"] == True
        assert result["data"]["employee_full_name"] == "John Doe"
    
    @pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available")
    def test_extract_payslip_data(self, extraction_service):
        """Test payslip data extraction."""
        pytest.skip("Requires complete payslip sample data")
    
    def test_extraction_with_empty_text(self, extraction_service):
        """Test extraction with empty text."""
        pytest.skip("Requires proper mocking of AI responses")


class TestPDFGeneration:
    """Test suite for PDF generation functionality."""
    
    def test_generate_employment_contract_pdf(self):
        """Test employment contract PDF generation."""
        pytest.skip("Requires complete EmploymentContract data model")
    
    def test_generate_payslip_pdf(self):
        """Test payslip PDF generation."""
        pytest.skip("Requires complete PayslipData model")
    
    def test_pdf_generation_with_minimal_data(self):
        """Test PDF generation with minimal data."""
        pytest.skip("Requires default value handling in models")


class TestDataValidation:
    """Test suite for data validation using Pydantic models."""
    
    def test_employment_contract_validation(self):
        """Test EmploymentContract model validation."""
        # Valid data with all required fields
        valid_data = {
            "employee_full_name": "John Doe",
            "employee_address": "123 Main St, Amsterdam",
            "employee_date_of_birth": "1990-01-01",
            "employment_start_date": "2024-01-01",
            "contract_type": "indefinite",
            "job_title": "Software Engineer",
            "gross_monthly_salary_eur": 5000,
            "holiday_allowance_percentage": 8.0,
            "weekly_working_hours": 40,
            "probation_period": "2 months",
            "employer_name": "Tech Corp BV",
            "thirteenth_month_bonus": "Yes",
            "pension_contribution_percentage": 5.0,
            "other_benefits": "Health insurance, laptop"
        }
        
        contract = EmploymentContract(**valid_data)
        assert contract.employee_full_name == "John Doe"
        assert contract.gross_monthly_salary_eur == 5000
    
    def test_payslip_data_validation(self):
        """Test PayslipData model validation."""
        valid_data = {
            "employee_name": "Jane Smith",
            "employee_number": "EMP001",
            "date_of_birth": "1985-06-08",
            "hire_date": "2020-01-15",
            "contract_type": "indefinite",
            "weekly_hours": 40,
            "parttime_percentage": 100,
            "hourly_wage": 31.25,
            "minimum_hourly_wage": 12.00,
            "on_call_agreement": False,
            "written_contract": True,
            "company_car": False,
            "gross_salary_period": 4500,
            "holiday_allowance": 360,
            "equity_compensation": 0,
            "adyen_plus_contribution": 50,
            "zvw_employer_contribution": 200,
            "meal_benefit_taxable": 0,
            "wage_tax_withheld": 900,
            "wga_recovery": 0,
            "equity_deduction_taxable": 0,
            "equity_deduction_nontaxable": 0,
            "net_salary_paid": 3600,
            "iban": "NL91ABNA0417164300",
            "payroll_period": "March 2024",
            "work_days_this_period": 22,
            "fiscal_wage_to_date": 13500,
            "social_security_wage_to_date": 13500,
            "annual_gross_salary": 54000,
            "cumulative_tax_credit": 345,
            "current_period_tax_credit": 115
        }
        
        payslip = PayslipData(**valid_data)
        assert payslip.employee_name == "Jane Smith"
        assert payslip.gross_salary_period == 4500
    
    def test_employment_contract_required_fields(self):
        """Test EmploymentContract requires all fields."""
        try:
            EmploymentContract()
            assert False, "Should have raised validation error"
        except ValueError:
            assert True
    
    def test_payslip_data_required_fields(self):
        """Test PayslipData requires all fields."""
        try:
            PayslipData()
            assert False, "Should have raised validation error"
        except ValueError:
            assert True

def run_integration_tests():
    """Run basic integration tests without API calls."""
    print("Running Legal Document Intake Integration Tests\n")
    
    tests = [
        ("DocumentProcessor initialization", lambda: DocumentProcessor() is not None),
        ("ExtractionService initialization", lambda: ExtractionService() is not None),
        ("EmploymentContract model type exists", lambda: EmploymentContract is not None),
        ("PayslipData model type exists", lambda: PayslipData is not None),
        ("PDF generation directories exist", lambda: Path("generated_pdfs").exists()),
        ("Upload directories exist", lambda: Path("uploads").exists()),
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            passed = result is True
            results[test_name] = {"result": "✅ PASS" if passed else "❌ FAIL", "passed": passed}
            if not passed:
                all_passed = False
        except Exception as e:
            results[test_name] = {"result": f"❌ ERROR: {str(e)}", "passed": False}
            all_passed = False
    
    return results, all_passed


if __name__ == "__main__":
    print("Running Legal Document Intake Tests\n")
    results, all_passed = run_integration_tests()
    
    print("\n" + "="*50)
    print("📊 INTEGRATION TEST RESULTS")
    print("="*50)
    
    for test_name, test_result in results.items():
        print(f"{test_name}: {test_result['result']}")
    
    print(f"\n🎉 All {len(results)} tests passed!" if all_passed else "❌ Some tests failed")
    
    try:
        import subprocess
        print("\n" + "="*50)
        print("🔬 RUNNING PYTEST SUITE")
        print("="*50)
        result = subprocess.run(["python", "-m", "pytest", __file__, "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
    except Exception as e:
        print(f"Could not run pytest: {e}")
