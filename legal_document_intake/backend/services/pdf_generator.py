import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Literal, Union

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, grey
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from ..schemas import EmploymentContract, PayslipData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PRIMARY_COLOR = HexColor("#2E86AB")
SECONDARY_COLOR = HexColor("#A23B72")
ACCENT_COLOR = HexColor("#F18F01")
TEXT_COLOR = HexColor("#333333")
LIGHT_GREY = HexColor("#F5F5F5")


class PDFGenerator:
    """Service for generating PDF reports from extracted document data."""
    
    def __init__(self, output_dir: str | Path = "generated_pdfs"):
        """
        Initialize the PDF generator.
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom styles for the PDF."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=20,
            spaceAfter=20,
            textColor=TEXT_COLOR,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=TEXT_COLOR,
            alignment=TA_LEFT
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=TEXT_COLOR,
            fontName='Helvetica-Bold'
        ))
        
        self.styles.add(ParagraphStyle(
            name='FieldValue',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=TEXT_COLOR,
            fontName='Helvetica'
        ))
        
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=grey,
            alignment=TA_CENTER
        ))
    
    def generate_employment_contract_pdf(
        self, 
        contract_data: EmploymentContract | Dict[str, Any], 
        job_id: str
    ) -> str:
        """
        Generate PDF report for employment contract data.
        
        Args:
            contract_data: Employment contract data
            job_id: Job identifier for filename
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating employment contract PDF for job: {job_id}")
        
        if isinstance(contract_data, EmploymentContract):
            data = contract_data.model_dump()
        else:
            data = contract_data
        
        filename = f"employment_contract_{job_id}.pdf"
        filepath = self.output_dir / filename
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        content = []
        
        content.append(Paragraph("Employment Contract Summary", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            self.styles['Normal']
        ))
        content.append(Paragraph(f"Job ID: {job_id}", self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Employee Information", self.styles['CustomSubtitle']))
        content.append(Paragraph(f"<b>Full Name:</b> {data.get('employee_full_name', 'N/A')}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Address:</b> {data.get('employee_address', 'N/A')}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Date of Birth:</b> {data.get('employee_date_of_birth', 'N/A')}", self.styles['Normal']))
        content.append(Paragraph(f"<b>Job Title:</b> {data.get('job_title', 'N/A')}", self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Employment Details", self.styles['CustomSubtitle']))
        content.append(Paragraph(f"<b>Start Date:</b> {data.get('employment_start_date', 'N/A')}", self.styles['Normal']))
        
        contract_type = data.get('contract_type', 'N/A')
        if hasattr(contract_type, 'value'):
            contract_type = contract_type.value
        elif str(contract_type).startswith('ContractType.'):
            contract_type = str(contract_type).replace('ContractType.', '').replace('_', ' ').title()
        content.append(Paragraph(f"<b>Contract Type:</b> {contract_type}", self.styles['Normal']))
        
        content.append(Paragraph(f"<b>Weekly Hours:</b> {data.get('weekly_working_hours', 'N/A')} hours", self.styles['Normal']))
        content.append(Paragraph(f"<b>Probation Period:</b> {data.get('probation_period', 'N/A')}", self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Compensation Details", self.styles['CustomSubtitle']))
        monthly_salary = f"€ {data.get('gross_monthly_salary_eur', 0):,.2f}" if data.get('gross_monthly_salary_eur') else 'N/A'
        content.append(Paragraph(f"<b>Monthly Salary:</b> {monthly_salary}", self.styles['Normal']))
        
        holiday_pct = f"{data.get('holiday_allowance_percentage', 'N/A')}%" if data.get('holiday_allowance_percentage') else 'N/A'
        content.append(Paragraph(f"<b>Holiday Allowance %:</b> {holiday_pct}", self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Benefits & Contributions", self.styles['CustomSubtitle']))
        pension_pct = f"{data.get('pension_contribution_percentage', 'N/A')}%" if data.get('pension_contribution_percentage') else 'N/A'
        content.append(Paragraph(f"<b>Pension Contribution %:</b> {pension_pct}", self.styles['Normal']))
        
        other_benefits = data.get('other_benefits', 'N/A')
        if other_benefits and other_benefits != 'N/A':
            content.append(Paragraph(f"<b>Other Benefits:</b>", self.styles['Normal']))
            
            if '•' in other_benefits:
                benefits_list = other_benefits.split('•')
                for benefit in benefits_list:
                    benefit = benefit.strip()
                    if benefit:
                        content.append(Paragraph(f"• {benefit}", self.styles['Normal']))
            else:
                content.append(Paragraph(other_benefits, self.styles['Normal']))
        else:
            content.append(Paragraph(f"<b>Other Benefits:</b> N/A", self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Employer Information", self.styles['CustomSubtitle']))
        content.append(Paragraph(f"<b>Employer Name:</b> {data.get('employer_name', 'N/A')}", self.styles['Normal']))
        
        content.append(Spacer(1, 40))
        content.append(Paragraph(
            "This document was automatically generated from the uploaded employment contract.",
            self.styles['Footer']
        ))
        
        doc.build(content)
        
        logger.info(f"Employment contract PDF generated: {filepath}")
        return str(filepath)
    
    def generate_payslip_pdf(
        self, 
        payslip_data: PayslipData | Dict[str, Any], 
        job_id: str
    ) -> str:
        """
        Generate PDF report for payslip data.
        
        Args:
            payslip_data: Payslip data
            job_id: Job identifier for filename
            
        Returns:
            Path to generated PDF file
        """
        logger.info(f"Generating payslip PDF for job: {job_id}")
        
        if isinstance(payslip_data, PayslipData):
            data = payslip_data.model_dump()
        else:
            data = payslip_data
        
        filename = f"payslip_{job_id}.pdf"
        filepath = self.output_dir / filename
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        content = []
        
        content.append(Paragraph("Payslip Summary", self.styles['CustomTitle']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph(
            f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
            self.styles['Normal']
        ))
        content.append(Paragraph(f"Job ID: {job_id}", self.styles['Normal']))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Employee Information", self.styles['CustomSubtitle']))
        employee_data = [
            ["Employee Name", data.get('employee_name', 'N/A')],
            ["Employee Number", data.get('employee_number', 'N/A')],
            ["Date of Birth", str(data.get('date_of_birth', 'N/A'))],
            ["Job Title", data.get('job_title', 'N/A')],
            ["IBAN", data.get('iban', 'N/A')],
        ]
        content.append(self._create_data_table(employee_data))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Employment Details", self.styles['CustomSubtitle']))
        employment_data = [
            ["Hire Date", str(data.get('hire_date', 'N/A'))],
            ["Contract Type", data.get('contract_type', 'N/A')],
            ["Weekly Hours", f"{data.get('weekly_hours', 'N/A')} hours"],
            ["Part-time %", f"{data.get('parttime_percentage', 'N/A')}%" if data.get('parttime_percentage') else 'N/A'],
            ["Hourly Wage", f"€{data.get('hourly_wage', 'N/A'):,.2f}" if data.get('hourly_wage') else 'N/A'],
        ]
        content.append(self._create_data_table(employment_data))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Current Period", self.styles['CustomSubtitle']))
        period_data = [
            ["Payroll Period", data.get('payroll_period', 'N/A')],
            ["Work Days", str(data.get('work_days_this_period', 'N/A'))],
            ["Gross Salary", f"€{data.get('gross_salary_period', 'N/A'):,.2f}" if data.get('gross_salary_period') else 'N/A'],
            ["Holiday Allowance", f"€{data.get('holiday_allowance', 'N/A'):,.2f}" if data.get('holiday_allowance') else 'N/A'],
            ["Net Salary Paid", f"€{data.get('net_salary_paid', 'N/A'):,.2f}" if data.get('net_salary_paid') else 'N/A'],
        ]
        content.append(self._create_data_table(period_data))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Deductions", self.styles['CustomSubtitle']))
        deductions_data = [
            ["Wage Tax", f"€{data.get('wage_tax_withheld', 'N/A'):,.2f}" if data.get('wage_tax_withheld') else 'N/A'],
            ["ZVW Contribution", f"€{data.get('zvw_employer_contribution', 'N/A'):,.2f}" if data.get('zvw_employer_contribution') else 'N/A'],
            ["WGA Recovery", f"€{data.get('wga_recovery', 'N/A'):,.2f}" if data.get('wga_recovery') else 'N/A'],
            ["Equity Deduction (Tax)", f"€{data.get('equity_deduction_taxable', 'N/A'):,.2f}" if data.get('equity_deduction_taxable') else 'N/A'],
        ]
        content.append(self._create_data_table(deductions_data))
        content.append(Spacer(1, 20))
        
        content.append(Paragraph("Year-to-Date Totals", self.styles['CustomSubtitle']))
        ytd_data = [
            ["Fiscal Wage YTD", f"€{data.get('fiscal_wage_to_date', 'N/A'):,.2f}" if data.get('fiscal_wage_to_date') else 'N/A'],
            ["Social Security YTD", f"€{data.get('social_security_wage_to_date', 'N/A'):,.2f}" if data.get('social_security_wage_to_date') else 'N/A'],
            ["Annual Gross Salary", f"€{data.get('annual_gross_salary', 'N/A'):,.2f}" if data.get('annual_gross_salary') else 'N/A'],
            ["Tax Credit YTD", f"€{data.get('cumulative_tax_credit', 'N/A'):,.2f}" if data.get('cumulative_tax_credit') else 'N/A'],
        ]
        content.append(self._create_data_table(ytd_data))
        
        content.append(Spacer(1, 40))
        content.append(Paragraph(
            "This document was automatically generated from the uploaded payslip.",
            self.styles['Footer']
        ))
        
        doc.build(content)
        
        logger.info(f"Payslip PDF generated: {filepath}")
        return str(filepath)
    
    def _create_data_table(self, data: list) -> Table:
        """Create a formatted table for data display."""
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_GREY),
            ('TEXTCOLOR', (0, 0), (-1, -1), TEXT_COLOR),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return table
    
    def generate_pdf(
        self, 
        document_data: Union[EmploymentContract, PayslipData, Dict[str, Any]], 
        document_type: Literal["employment_contract", "payslip"], 
        job_id: str
    ) -> str:
        """
        Generate PDF for any document type.
        
        Args:
            document_data: Document data
            document_type: Type of document
            job_id: Job identifier
            
        Returns:
            Path to generated PDF file
        """
        if document_type == "employment_contract":
            return self.generate_employment_contract_pdf(document_data, job_id)
        elif document_type == "payslip":
            return self.generate_payslip_pdf(document_data, job_id)
        else:
            raise ValueError(f"Unsupported document type: {document_type}")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """Remove old PDF files."""
        import time
        
        current_time = time.time()
        cutoff_time = current_time - (max_age_hours * 3600)
        
        for pdf_file in self.output_dir.glob("*.pdf"):
            if pdf_file.stat().st_mtime < cutoff_time:
                try:
                    pdf_file.unlink()
                    logger.info(f"Cleaned up old PDF: {pdf_file}")
                except Exception as e:
                    logger.warning(f"Failed to clean up {pdf_file}: {e}")


def generate_employment_contract_pdf(
    contract_data: Union[EmploymentContract, Dict[str, Any]], 
    job_id: str,
    output_dir: str | Path = "generated_pdfs"
) -> str:
    """
    Convenience function to generate employment contract PDF.
    
    Args:
        contract_data: Employment contract data
        job_id: Job identifier
        output_dir: Output directory
        
    Returns:
        Path to generated PDF
    """
    generator = PDFGenerator(output_dir)
    return generator.generate_employment_contract_pdf(contract_data, job_id)


def generate_payslip_pdf(
    payslip_data: Union[PayslipData, Dict[str, Any]], 
    job_id: str,
    output_dir: str | Path = "generated_pdfs"
) -> str:
    """
    Convenience function to generate payslip PDF.
    
    Args:
        payslip_data: Payslip data
        job_id: Job identifier
        output_dir: Output directory
        
    Returns:
        Path to generated PDF
    """
    generator = PDFGenerator(output_dir)
    return generator.generate_payslip_pdf(payslip_data, job_id)
