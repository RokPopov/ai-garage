from pydantic import BaseModel, Field, validator
from typing import Literal
from datetime import date
from enum import Enum
import re


class ContractType(str, Enum):
    FIXED_TERM = "fixed-term"
    INDEFINITE = "indefinite"
    OTHER = "other"


class EmploymentContract(BaseModel):
    """Pydantic model for employment contract data extraction"""
    
    employee_full_name: str = Field(..., description="Full name of the employee", min_length=1)
    employee_address: str = Field(..., description="Employee's residential address", min_length=1)
    employee_date_of_birth: date = Field(..., description="Employee's date of birth")
    employment_start_date: date = Field(..., description="Start date of employment")
    contract_type: ContractType = Field(..., description="Type of employment contract")
    job_title: str = Field(..., description="Employee's job title/position", min_length=1)
    gross_monthly_salary_eur: float = Field(..., description="Monthly gross salary in EUR", gt=0)
    holiday_allowance_percentage: float = Field(..., description="Holiday allowance as percentage", ge=0, le=100)
    weekly_working_hours: float = Field(..., description="Weekly working hours", gt=0, le=168)
    probation_period: str = Field(..., description="Probation period duration")
    employer_name: str = Field(..., description="Name of the employer/company", min_length=1)
    thirteenth_month_bonus: str = Field(..., description="13th month bonus details")
    pension_contribution_percentage: float = Field(..., description="Pension contribution as percentage", ge=0, le=100)
    other_benefits: str = Field(..., description="Other benefits and perks")
    
    @validator('employee_date_of_birth')
    def validate_birth_date(cls, v):
        if v >= date.today():
            raise ValueError('Birth date must be in the past')
        return v
    
    @validator('employment_start_date')
    def validate_start_date(cls, v):
        if v > date.today():
            from datetime import timedelta
            if v > date.today() + timedelta(days=365):
                raise ValueError('Start date cannot be more than 1 year in the future')
        return v

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "employee_full_name": "John Doe",
                "employee_address": "123 Main Street, Amsterdam, 1000AA",
                "employee_date_of_birth": "1990-01-15",
                "employment_start_date": "2024-01-01",
                "contract_type": "indefinite",
                "job_title": "Software Engineer",
                "gross_monthly_salary_eur": 5000.0,
                "holiday_allowance_percentage": 8.0,
                "weekly_working_hours": 40.0,
                "probation_period": "2 months",
                "employer_name": "Tech Company B.V.",
                "thirteenth_month_bonus": "Yes, paid in December",
                "pension_contribution_percentage": 4.5,
                "other_benefits": "Health insurance, laptop, travel allowance"
            }
        }


class PayslipData(BaseModel):
    """Pydantic model for payslip data extraction"""
    
    employee_name: str = Field(..., description="Employee name from payslip", min_length=1)
    employee_number: str = Field(..., description="Employee number/ID", min_length=1)
    date_of_birth: date = Field(..., description="Employee's date of birth")
    hire_date: date = Field(..., description="Employee's hire date")
    contract_type: str = Field(..., description="Type of employment contract", min_length=1)
    weekly_hours: float = Field(..., description="Weekly working hours", gt=0, le=168)
    parttime_percentage: float = Field(..., description="Part-time percentage", gt=0, le=100)
    hourly_wage: float = Field(..., description="Hourly wage rate", gt=0)
    minimum_hourly_wage: float = Field(..., description="Minimum hourly wage", gt=0)
    on_call_agreement: bool = Field(..., description="On-call agreement status")
    written_contract: bool = Field(..., description="Written contract status")
    company_car: bool = Field(..., description="Company car availability")
    gross_salary_period: float = Field(..., description="Gross salary for the period", gt=0)
    holiday_allowance: float = Field(..., description="Holiday allowance amount", ge=0)
    equity_compensation: float = Field(..., description="Equity compensation", ge=0)
    adyen_plus_contribution: float = Field(..., description="Adyen+ contribution", ge=0)
    zvw_employer_contribution: float = Field(..., description="ZVW employer contribution", ge=0)
    meal_benefit_taxable: float = Field(..., description="Meal benefit (taxable)", ge=0)
    wage_tax_withheld: float = Field(..., description="Wage tax withheld", ge=0)
    wga_recovery: float = Field(..., description="WGA recovery amount", ge=0)
    equity_deduction_taxable: float = Field(..., description="Equity deduction (taxable)", ge=0)
    equity_deduction_nontaxable: float = Field(..., description="Equity deduction (non-taxable)", ge=0)
    net_salary_paid: float = Field(..., description="Net salary paid", gt=0)
    iban: str = Field(..., description="Bank account IBAN", min_length=1)
    payroll_period: str = Field(..., description="Payroll period", min_length=1)
    work_days_this_period: float = Field(..., description="Work days in this period", gt=0, le=31)
    fiscal_wage_to_date: float = Field(..., description="Fiscal wage to date", ge=0)
    social_security_wage_to_date: float = Field(..., description="Social security wage to date", ge=0)
    annual_gross_salary: float = Field(..., description="Annual gross salary", gt=0)
    cumulative_tax_credit: float = Field(..., description="Cumulative tax credit", ge=0)
    current_period_tax_credit: float = Field(..., description="Current period tax credit", ge=0)
    
    @validator('iban')
    def validate_iban(cls, v):
        # Basic IBAN validation for Netherlands
        if not re.match(r'^NL\d{2}[A-Z]{4}\d{10}$', v):
            raise ValueError('Invalid Dutch IBAN format')
        return v
    
    @validator('date_of_birth')
    def validate_birth_date(cls, v):
        if v >= date.today():
            raise ValueError('Birth date must be in the past')
        return v
    
    @validator('hire_date')
    def validate_hire_date(cls, v):
        if v > date.today():
            from datetime import timedelta
            if v > date.today() + timedelta(days=365):
                raise ValueError('Hire date cannot be more than 1 year in the future')
        return v

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "employee_name": "John Doe",
                "employee_number": "EMP001",
                "date_of_birth": "1990-01-15",
                "hire_date": "2024-01-01",
                "contract_type": "indefinite",
                "weekly_hours": 40.0,
                "parttime_percentage": 100.0,
                "hourly_wage": 31.25,
                "minimum_hourly_wage": 12.00,
                "on_call_agreement": False,
                "written_contract": True,
                "company_car": False,
                "gross_salary_period": 5000.0,
                "holiday_allowance": 400.0,
                "equity_compensation": 0.0,
                "adyen_plus_contribution": 50.0,
                "zvw_employer_contribution": 200.0,
                "meal_benefit_taxable": 0.0,
                "wage_tax_withheld": 1200.0,
                "wga_recovery": 0.0,
                "equity_deduction_taxable": 0.0,
                "equity_deduction_nontaxable": 0.0,
                "net_salary_paid": 3550.0,
                "iban": "NL02ABNA0123456789",
                "payroll_period": "2024-01",
                "work_days_this_period": 22.0,
                "fiscal_wage_to_date": 5000.0,
                "social_security_wage_to_date": 5000.0,
                "annual_gross_salary": 60000.0,
                "cumulative_tax_credit": 100.0,
                "current_period_tax_credit": 100.0
            }
        }


class ProcessingState(BaseModel):
    """State model for LangGraph workflow processing"""
    
    job_id: str = Field(..., description="Unique job identifier", min_length=1)
    document_type: Literal["employment_contract", "payslip"] = Field(..., description="Type of document being processed")
    file_path: str = Field(..., description="Path to uploaded file", min_length=1)
    extracted_text: str | None = Field(None, description="Extracted text from document")
    structured_data: dict | None = Field(None, description="Extracted structured data")
    processing_status: Literal["pending", "processing", "completed", "failed"] = Field(default="pending", description="Current processing status")
    error_message: str | None = Field(None, description="Error message if processing failed")
    pdf_path: str | None = Field(None, description="Path to generated PDF file")
    
    current_node: str | None = Field(None, description="Current workflow node")
    processing_metadata: dict = Field(default_factory=dict, description="Processing metadata and intermediate results")
    retry_count: int = Field(default=0, description="Number of retry attempts")
    
    def update_status(self, status: Literal["pending", "processing", "completed", "failed"], node: str | None = None):
        """Update processing status and current node"""
        self.processing_status = status
        if node:
            self.current_node = node

    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "job_123456",
                "document_type": "employment_contract",
                "file_path": "/uploads/contract.pdf",
                "processing_status": "pending"
            }
        }
