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
            "Employee contribution different from the contribution base rounded to the euro × the position's rate "
            "(pensions, CIGS, FIS), plus 1% above the first pensionable band",
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
    "C15": ("INPS sick pay",
            "Sick pay advanced for INPS different from 50% (days 4-20) and 66.66% (days 21-180) of last month's "
            "average daily pay",
            "Recompute on last month's pay × 14/12 / 30, at 50% from day 4 to 20 and 66.66% after, and correct the "
            "offset in the UniEmens return"),
    "C16": ("Sick-leave waiting days",
            "The first 3 days topped up from the 5th sickness of the year, or not topped up when they are due",
            "Count the year's sicknesses: from the fifth the waiting days are not paid, unless hospital, a first "
            "prognosis of 12 days or more, life-saving treatment or pregnancy; if due and missing, pay them"),
    "C17": ("INPS maternity pay",
            "Maternity pay advanced for INPS different from 80% of last month's average daily pay",
            "Recompute at 80% of average daily pay, accruals included, and correct the offset with INPS; the top-up "
            "to 100% stays with the employer"),
    "C18": ("Paid leave hours (ROL and former holidays)",
            "Hours balance different from last month's + hours accrued − hours taken, with the CCNL accrual",
            "Redo the accrual: 72 or 56 hours of working-time reduction by headcount, plus 32 of former holidays, "
            "pro rata for part-time, with the 2- and 4-year rule for staff hired after March 2011"),
    "C19": ("Severance pay at leaving (TFR)",
            "TFR different from the fund revalued with the ISTAT index, net of the substitute tax, plus the year's "
            "accruals less 0.50%",
            "Redo the sum: ISTAT coefficient of the right month (from the 15th the month counts), 17% substitute tax "
            "on the revaluation, 0.50% off the year's accruals; settle the difference"),
    "C20": ("Income tax of the month (IRPEF)",
            "Tax withheld, tax-wedge payment or supplementary allowance different from the 2026 rules: annual "
            "brackets scaled to the month, credits for a twelfth of the year's expected income",
            "Check the payroll software's tax table (33% in the second bracket from 2026), the extra credit and the "
            "tax-wedge payment, the supplementary allowance; redo the withholding and correct it next month"),
    "C21": ("Income tax adjustment at leaving",
            "The year's tax, with credits and supplementary allowance in proportion to the days worked, less what "
            "was withheld or paid: the leaver's payslip carries a different difference",
            "Redo the adjustment: the year's tax on taxable pay since January, credits and allowance for the days "
            "worked, less what was already withheld or paid; hand the workings over with the CU"),
}

PRIORITA_EN = {"alta": "high", "media": "medium"}
