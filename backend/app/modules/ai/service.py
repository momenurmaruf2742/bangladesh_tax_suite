from pydantic import BaseModel


class AiChatRequest(BaseModel):
    prompt: str


class AiChatResponse(BaseModel):
    reply: str
    key_points: list[str]
    reference_laws: list[str]


class AiTaxService:
    @staticmethod
    def get_tax_advice(prompt: str) -> AiChatResponse:
        """Provide domain-specific Bangladesh tax advisory based on Income Tax Act 2023."""
        text = prompt.lower()

        # 1. DPS Investment Rebate Rules
        if "dps" in text or "deposit pension" in text:
            reply = (
                "Under Section 78 of the Bangladesh Income Tax Act 2023, investments in Deposit Pension Scheme (DPS) "
                "are eligible for investment tax rebate. However, the maximum allowable investment in DPS is capped at "
                "BDT 1,20,000 (1.2 Lakh) per financial year. You will receive a 15% tax rebate on your eligible investment."
            )
            key_points = [
                "Max eligible DPS investment: BDT 1,20,000 / year",
                "Rebate Rate: 15% of eligible investment amount",
                "Max rebate from DPS alone: BDT 18,000"
            ]
            reference_laws = ["Income Tax Act 2023 - Section 78", "Sixth Schedule Part 2"]

        # 2. Basic Tax Free Thresholds
        elif "threshold" in text or "tax free" in text or "limit" in text or "slab" in text:
            reply = (
                "For Assessment Year 2025-26, the general tax-free income threshold is BDT 3,50,000. "
                "For female taxpayers and senior citizens (aged 65+), the threshold is BDT 4,00,000. "
                "For disabled taxpayers, it is BDT 4,75,000, and for Gazetted Freedom Fighters, it is BDT 5,00,000."
            )
            key_points = [
                "General Taxpayers: BDT 3,50,000",
                "Female & Senior Citizens (65+): BDT 4,00,000",
                "Disabled Persons: BDT 4,75,000",
                "Gazetted Freedom Fighters: BDT 5,00,000",
                "Tax Slabs: First slab 0%, next 1L @ 5%, next 3L @ 10%, next 4L @ 15%, next 5L @ 20%, balance @ 25%"
            ]
            reference_laws = ["Finance Act 2024 / Income Tax Act 2023 First Schedule"]

        # 3. Salary Allowance Exemptions
        elif "salary" in text or "house rent" in text or "medical" in text or "conveyance" in text:
            reply = (
                "Under the Income Tax Act 2023, standard salary exemptions apply: "
                "1/3rd of Total Gross Salary OR BDT 4,50,000 (whichever is lower) is exempted from taxable income. "
                "Separate old rules for House Rent (50%) and Medical (10%) have been unified into this single lower cap."
            )
            key_points = [
                "Unified Exemption: Lower of 1/3rd Gross Salary OR BDT 4,50,000",
                "House Rent, Medical, Conveyance allowances are included in gross calculation",
                "Festival bonuses are fully taxable"
            ]
            reference_laws = ["Income Tax Act 2023 - Part 4 (Salaries)"]

        # 4. Sanchayapatra & Life Insurance
        elif "sanchayapatra" in text or "insurance" in text or "stock" in text or "rebate" in text:
            reply = (
                "Total allowable investment rebate is 15% of the lowest of: "
                "1) Actual total eligible investments (Sanchayapatra, DPS, Stock Market, Life Insurance, PF), "
                "2) 20% of Total Taxable Income, or "
                "3) Absolute cap of BDT 10,00,000 (10 Lakh)."
            )
            key_points = [
                "Eligible Sectors: Sanchayapatra, DPS (max 1.2L), Life Insurance, Approved Stocks, PF",
                "Rebate Percentage: 15%",
                "Max Absolute Rebate Cap: BDT 10,00,000"
            ]
            reference_laws = ["Income Tax Act 2023 - Section 78"]

        # 5. General fallback tax guidance
        else:
            reply = (
                f"Hello! I am your AI Tax Assistant grounded in the Bangladesh Income Tax Act 2023. "
                f"Regarding your query: '{prompt}', I can assist you with tax-free thresholds, salary allowance exemptions, "
                f"Section 78 investment rebates (DPS, Sanchayapatra, Insurance), AIT/TDS deductions, and filing rules."
            )
            key_points = [
                "Enter your salary slips to calculate taxable income automatically",
                "Add your DPS and Sanchayapatra investments to claim up to 15% tax rebate",
                "Download official PDF Computation Sheet for NBR filing"
            ]
            reference_laws = ["Income Tax Act 2023 Rules Engine"]

        return AiChatResponse(
            reply=reply,
            key_points=key_points,
            reference_laws=reference_laws
        )
