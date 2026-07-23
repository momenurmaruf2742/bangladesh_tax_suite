import io
import re
from pypdf import PdfReader


class OcrService:
    @staticmethod
    def parse_salary_pdf(pdf_bytes: bytes) -> dict:
        """Extract text from uploaded Salary Slip or Certificate PDF using pypdf and regex pattern matching."""
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            
            if not extracted_text.strip():
                return {
                    "success": False,
                    "message": "No readable text found in PDF. File might be a scanned image.",
                    "data": {}
                }

            text_lower = extracted_text.lower()

            # Helper regex extractor for currency amounts
            def extract_amount(patterns: list[str]) -> float:
                for pattern in patterns:
                    match = re.search(pattern, extracted_text, re.IGNORECASE)
                    if match:
                        num_str = match.group(1).replace(",", "").replace("=", "").strip()
                        try:
                            return float(num_str)
                        except ValueError:
                            continue
                return 0.0

            # Regex patterns for standard Bangladeshi Salary Certificate & Slip structures
            basic = extract_amount([
                r"basic\s*(?:salary)?\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)",
                r"moulika?\s*[:=-]?\s*([\d,]+\.?\d*)"
            ])
            
            house_rent = extract_amount([
                r"house\s*rent\s*(?:allowance)?\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)",
                r"bari\s*bhad?a\s*[:=-]?\s*([\d,]+\.?\d*)"
            ])
            
            medical = extract_amount([
                r"medical\s*(?:allowance)?\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)",
                r"chikitsa\s*[:=-]?\s*([\d,]+\.?\d*)"
            ])

            conveyance = extract_amount([
                r"(?:conveyance|transport)\s*(?:allowance)?\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)",
                r"yabayata\s*[:=-]?\s*([\d,]+\.?\d*)"
            ])

            festival_bonus = extract_amount([
                r"(?:festival|eid)\s*bonus\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)"
            ])

            tds_deducted = extract_amount([
                r"(?:tds|ait|income\s*tax)\s*(?:deducted|paid)?\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)",
                r"tax\s*deducted\s*at\s*source\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)"
            ])

            gross_salary = extract_amount([
                r"gross\s*(?:salary|pay)?\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)",
                r"total\s*(?:salary|earnings)?\s*[:=-]?\s*(?:bdt|৳)?\s*([\d,]+\.?\d*)"
            ])

            # Extract Financial Year if present (e.g. FY 2025-26, 2025-2026)
            fy_match = re.search(r"(?:fy|financial\s*year)\s*[:=-]?\s*(20\d{2}\s*[-/]\s*(?:20)?\d{2})", extracted_text, re.IGNORECASE)
            financial_year = fy_match.group(1).replace(" ", "") if fy_match else "2025-2026"

            # If gross salary was missing but basic exists, compute sum
            calculated_gross = basic + house_rent + medical + conveyance + festival_bonus
            if gross_salary == 0.0 and calculated_gross > 0:
                gross_salary = calculated_gross

            return {
                "success": True,
                "message": "Successfully parsed salary PDF document using OCR text recognition.",
                "data": {
                    "basic": basic,
                    "house_rent": house_rent,
                    "medical": medical,
                    "conveyance": conveyance,
                    "festival_bonus": festival_bonus,
                    "other_allowance": 0.0,
                    "gross_salary": gross_salary,
                    "tds_deducted": tds_deducted,
                    "financial_year": financial_year,
                    "extracted_text_preview": extracted_text[:300] + "..." if len(extracted_text) > 300 else extracted_text
                }
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to parse PDF document: {str(e)}",
                "data": {}
            }
