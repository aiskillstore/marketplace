"""Entirely invented fixtures. This module never reads personal files."""
from calendar import monthrange


def make_demo(language="en"):
    rows = []
    def add(day, description, amount, kind="expense", group="daily", category="Groceries", account="Demo checking", share=1):
        row = dict(id=f"fiction-{len(rows)+1:04}", date=day, description=description,
                   amount=f"{amount:.2f}", kind=kind, group=group, category=category,
                   account=account, source=f"Fictional example row {len(rows)+1}", share=share,
                   incomeType="salary" if description=="Demo employer" else "support" if description=="Demo household allowance" else "other",
                   purpose="loan" if "loan" in description or "repayment" in description else "other")
        rows.append(row)
        return row["id"]
    for m in range(1, 4):
        d = lambda day: f"2024-{m:02}-{day:02}"
        add(d(2), "Demo employer", 4200, "income", "other", "Salary")
        add(d(17), "Demo weekend project", 180 + 35*m, "income", "other", "Freelance")
        add(d(10), "Demo household allowance", 350, "income", "other", "Living allowance")
        add(d(3), "Fictional home rent", -1560, group="housing", category="Rent", share=.5)
        add(d(8), "Fictional home internet", -64, group="housing", category="Internet", share=.5)
        add(d(12), "Fictional utility provider", -92-8*m, group="housing", category="Utilities", share=.5)
        add(d(6), "Example music service", -11.50, group="fixed", category="Music")
        add(d(14), "Example cloud notes", -7, group="fixed", category="Software")
        add(d(15), "Example language model", -23, group="ai", category="AI tools")
        for day in range(1, monthrange(2024,m)[1]+1):
            if day % 3 == 0: add(d(day), ["Fictional corner market", "Example village grocer", "Sample produce shop"][(day//3)%3], -(24 + (day*7+m*13)%65), category="Groceries")
            if day % 4 == 0: add(d(day), ["Fictional lunch cafe", "Example noodle cafe", "Sample tea shop"][(day//4)%3], -(12 + (day*3+m)%24), category="Dining")
            if day % 5 == 0: add(d(day), "Fictional transit pass", -9.50, category="Transport")
            if day % 11 == 0: add(d(day), "Fictional bookshop", -(15+m*4), category="Shopping")
        add(d(9), "Fictional household supplies", -14.25, category="Other")
        add(d(13), "Fictional unresolved shop receipt", -8.40, category="Uncategorized")
        add(d(20), "Own savings move", -350, "internal", "other", "Own transfer")
        add(d(20), "Own savings move", 350, "internal", "other", "Own transfer", "Demo savings")
        add(d(22), "Unknown incoming payment", 65, "transfer_in", "other", "Needs review")
    purchase = add("2024-02-23", "Fictional returned desk lamp", -84, category="Shopping")
    refund = add("2024-03-04", "Fictional lamp refund", 84, "refund", "other", "Refund")
    add("2024-03-11", "Unpaired fictional refund", 18, "refund", "other", "Needs review")
    loan = add("2024-01-25", "Confirmed demo loan", -120, "transfer_out", "other", "Loan")
    paid = add("2024-03-09", "Confirmed demo partial repayment", 50, "transfer_in", "other", "Loan repayment")
    add("2024-03-19", "Unclassified fictional transfer", -45, "transfer_out", "other", "Needs review")
    add("2024-03-24", "Fictional course materials", -96, group="education", category="Study")
    return dict(schemaVersion=1, currency="USD", language=language,
                coverage=dict(start="2024-01-01", end="2024-03-31"), transactions=rows,
                refunds=[dict(purchaseId=purchase, refundIds=[refund])],
                settlements=[dict(outId=loan, inId=paid, amount="50.00")],
                notes=["Every name, date, amount and record in this demo is invented." if language == "en" else "演示中的姓名、日期、金额和记录均为虚构。"], demo=True)

if __name__ == "__main__":
    import json
    print(json.dumps(make_demo(), ensure_ascii=False, indent=2))
