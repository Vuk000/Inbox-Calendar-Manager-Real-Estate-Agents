"""
Document processing service for PDF extraction and summarization
"""
from typing import Dict, Any, Optional
import PyPDF2
import io
from anthropic import Anthropic
from ..config import settings
import json


class DocumentProcessor:
    """
    Process PDF documents - extract text, summarize with AI.
    Real estate document intelligence.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_bytes: PDF file content as bytes
            
        Returns:
            Extracted text
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    async def summarize_document(
        self,
        document_text: str,
        document_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Summarize a real estate document using AI.
        
        Args:
            document_text: Extracted document text
            document_type: Type of document (contract, inspection, appraisal, disclosure)
            
        Returns:
            Dictionary with summary and extracted information
        """
        prompt = f"""You are a real estate document analysis expert. Analyze this {document_type} document and provide a comprehensive summary.

Document Text:
{document_text[:8000]}  # Limit to avoid token overflow

Provide analysis in JSON format:

1. **document_type_confirmed** (string): Confirm the type (contract, inspection, appraisal, disclosure, other)

2. **summary** (string): 3-5 sentence summary of the document

3. **key_parties** (object):
   - buyer (string or null)
   - seller (string or null)
   - agent (string or null)
   - lender (string or null)
   - inspector (string or null)

4. **property_details** (object):
   - address (string or null)
   - price (number or null)
   - property_type (string or null)

5. **financial_details** (object):
   - purchase_price (number or null)
   - earnest_money (number or null)
   - down_payment (number or null)
   - loan_amount (number or null)
   - closing_costs (number or null)
   - other_amounts (array): Other significant amounts mentioned

6. **key_dates** (object):
   - contract_date (string ISO or null)
   - inspection_deadline (string ISO or null)
   - financing_deadline (string ISO or null)
   - closing_date (string ISO or null)
   - other_deadlines (array): Other important dates

7. **contingencies** (array): List of contingencies mentioned

8. **issues_flagged** (array): Any problems, concerns, or red flags
   - For inspections: structural issues, repairs needed, cost estimates
   - For contracts: unusual terms, risky clauses
   - For appraisals: value concerns, market conditions

9. **action_items** (array): Required actions or next steps

10. **risk_level** (string): "low", "medium", "high" - overall risk assessment

11. **confidence** (float 0-1): Confidence in this analysis

Return ONLY valid JSON:"""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=settings.ANTHROPIC_MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            analysis = json.loads(response_text)
            
            return analysis
            
        except Exception as e:
            return {
                "document_type_confirmed": document_type,
                "summary": "Failed to analyze document",
                "error": str(e),
                "key_parties": {},
                "property_details": {},
                "financial_details": {},
                "key_dates": {},
                "contingencies": [],
                "issues_flagged": [],
                "action_items": [],
                "risk_level": "unknown",
                "confidence": 0.0
            }
    
    def extract_property_address(self, text: str) -> Optional[str]:
        """
        Extract property address from document text.
        Simple regex-based extraction.
        """
        import re
        
        # Pattern for street addresses
        pattern = r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Way|Court|Ct|Place|Pl|Circle|Cir)'
        
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        if matches:
            return matches[0]
        
        return None
    
    async def detect_compliance_issues(
        self,
        document_analysis: Dict[str, Any],
        transaction_stage: str
    ) -> Dict[str, Any]:
        """
        Check for compliance issues based on transaction stage.
        
        Args:
            document_analysis: Document analysis from AI
            transaction_stage: Current stage (offer, under_contract, closing, etc.)
            
        Returns:
            Compliance check results
        """
        issues = []
        
        # Check for missing information
        key_dates = document_analysis.get("key_dates", {})
        
        if transaction_stage == "under_contract":
            if not key_dates.get("inspection_deadline"):
                issues.append({
                    "type": "missing_deadline",
                    "severity": "medium",
                    "message": "Inspection deadline not found in contract"
                })
            
            if not key_dates.get("financing_deadline"):
                issues.append({
                    "type": "missing_deadline",
                    "severity": "medium",
                    "message": "Financing deadline not specified"
                })
        
        # Check risk level
        risk_level = document_analysis.get("risk_level", "unknown")
        if risk_level == "high":
            issues.append({
                "type": "high_risk",
                "severity": "high",
                "message": "Document flagged as high risk - review carefully",
                "details": document_analysis.get("issues_flagged", [])
            })
        
        # Check for cost overruns (inspection reports)
        flagged_issues = document_analysis.get("issues_flagged", [])
        for issue in flagged_issues:
            if "$" in str(issue) and any(word in str(issue).lower() for word in ["repair", "fix", "cost", "damage"]):
                issues.append({
                    "type": "cost_alert",
                    "severity": "medium",
                    "message": f"Potential cost issue: {issue}"
                })
        
        return {
            "has_issues": len(issues) > 0,
            "issue_count": len(issues),
            "issues": issues,
            "transaction_stage": transaction_stage
        }

