"""
English texts for the browser tool. The Italian ones are in controlli.CONTROLLI and build_rapporto.COSA_FARE;
build_web.write_texts() puts both in web/testi.json, and a test fails if a check has no English text.
"""

CONTROLLI_EN = {
    "C01": ("Minimum basic pay",
            "Basic pay different from the grade minimum (base pay, other elements, cost-of-living allowance), "
            "part-time included",
            "Bring basic pay up to the current minimum and pay the arrears"),
    "C02": ("Seniority increments",
            "Seniority increments different from those earned since the hiring date",
            "Add the increment earned and check the date it starts from"),
    "C03": ("Social security (INPS)",
            "Employee contribution different from the contribution base rounded to the euro × rate",
            "Correct the rate in the employee's INPS position"),
    "C04": ("Severance accrual (TFR)",
            "Monthly TFR accrual different from ordinary pay × 14 / 13.5 / 12",
            "Recompute the accrual including increments and the individual supplement"),
    "C05": ("Holiday balance",
            "Balance different from last month's balance + days accrued − days taken",
            "Realign the balance: this month's accrual was not recorded"),
    "C06": ("Payslip arithmetic",
            "Gross different from the sum of its items, or net different from gross minus deductions",
            "Recheck the items: the payslip does not add up"),
    "C07": ("Change in net pay",
            "Net pay more than 20% above or below last month, with no event to explain it",
            "Ask the client for the event behind the change"),
    "C08": ("F24 reconciliation",
            "Taxes or contributions in the F24 different from the sum of the client's payslips",
            "Complete the F24 before the payment deadline"),
    "C09": ("Tax code",
            "The tax code's check character is not valid",
            "Correct the tax code in the personnel records"),
    "C10": ("Personnel records",
            "Grade, part-time, individual supplement or hiring date changed since last month, with no event",
            "Check the change with the client and the documents; if it did not happen, correct the records"),
    "C11": ("13th and 14th month accruals",
            "Twelfths earned different from the months of service in the period (15 days count as a month)",
            "Recount the twelfths from the hiring date and correct the accruals before December's 13th month"),
    "C12": ("13th and 14th month paid",
            "Amount different from monthly pay × twelfths earned, in December or when employment ends",
            "Recompute with the right twelfths (from January for the 13th, from July for the 14th) and settle the "
            "difference: pay it if short, recover it if overpaid"),
    "C13": ("Untaken holiday",
            "Untaken holiday paid at leaving different from monthly pay / 26 × days left",
            "Recompute untaken holiday at 1/26 of monthly pay per day and settle the difference: pay it if short, "
            "recover it if overpaid"),
    "C14": ("Notice period",
            "Notice shorter than the CCNL minimum for grade, years of service and who ends the contract",
            "Check the date of the letter. Dismissal: notice days not worked are paid as an allowance. Resignation: "
            "notice not given can be withheld as an allowance owed by the employee"),
}

PRIORITA_EN = {"alta": "high", "media": "medium"}
