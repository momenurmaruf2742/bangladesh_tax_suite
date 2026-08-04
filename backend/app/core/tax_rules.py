from decimal import Decimal

from fastapi import HTTPException, status

TAX_YEAR_RULES = {
    "2024-2025": {
        "exemption_rate": Decimal("3.0"),
        "exemption_max": Decimal("450000.00"),
        "dps_max": Decimal("120000.00"),
        "rebate_rate": Decimal("0.15"),
        "income_rebate_limit_rate": Decimal("0.03"),
        "max_rebate_cap": Decimal("1000000.00"),
        "max_eligible_invest_rate": Decimal("0.20"),
        "max_eligible_invest_cap": Decimal("6666666.67"),
        "thresholds": {
            "default": Decimal("350000.00"),
            "Female": Decimal("400000.00"),
            "Third Gender": Decimal("400000.00"),
            "is_disabled": Decimal("475000.00"),
            "is_freedom_fighter": Decimal("500000.00"),
        },
        "slabs": [
            ("Tax-free limit", Decimal("0.0"), Decimal("0.0")),
            ("Next 1,00,000 BDT", Decimal("100000.00"), Decimal("0.05")),
            ("Next 3,00,000 BDT", Decimal("300000.00"), Decimal("0.10")),
            ("Next 4,00,000 BDT", Decimal("400000.00"), Decimal("0.15")),
            ("Next 5,00,000 BDT", Decimal("500000.00"), Decimal("0.20")),
            ("Remaining taxable balance", None, Decimal("0.25")),
        ],
        "minimum_tax_location_based": True,
        "minimum_tax": {
            "Dhaka/Chittagong City Corporation": Decimal("5000.00"),
            "Other City Corporation": Decimal("4000.00"),
            "default": Decimal("3000.00"),
        },
    },
    "2025-2026": {
        "exemption_rate": Decimal("3.0"),
        "exemption_max": Decimal("450000.00"),
        "dps_max": Decimal("120000.00"),
        "rebate_rate": Decimal("0.10"),
        "income_rebate_limit_rate": Decimal("0.03"),
        "max_rebate_cap": Decimal("750000.00"),
        "max_eligible_invest_rate": Decimal("0.20"),
        "max_eligible_invest_cap": Decimal("7500000.00"),
        "thresholds": {
            "default": Decimal("400000.00"),
            "Female": Decimal("425000.00"),
            "Third Gender": Decimal("425000.00"),
            "is_disabled": Decimal("475000.00"),
            "is_freedom_fighter": Decimal("525000.00"),
        },
        "slabs": [
            ("Tax-free limit", Decimal("0.0"), Decimal("0.0")),
            ("Next 3,00,000 BDT", Decimal("300000.00"), Decimal("0.10")),
            ("Next 4,00,000 BDT", Decimal("400000.00"), Decimal("0.15")),
            ("Next 5,00,000 BDT", Decimal("500000.00"), Decimal("0.20")),
            ("Next 20,00,000 BDT", Decimal("2000000.00"), Decimal("0.25")),
            ("Remaining taxable balance", None, Decimal("0.30")),
        ],
        "minimum_tax_location_based": False,
        "minimum_tax": {
            "default": Decimal("5000.00"),
        },
    },
}

# 2026-2027 uses the same rules as 2025-2026 for now
TAX_YEAR_RULES["2026-2027"] = TAX_YEAR_RULES["2025-2026"]


def get_tax_rules(financial_year: str) -> dict:
    if financial_year not in TAX_YEAR_RULES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Financial year '{financial_year}' is not supported. Supported years: {', '.join(TAX_YEAR_RULES.keys())}",
        )
    return TAX_YEAR_RULES[financial_year]
