#!/usr/bin/env python3
"""
Example usage of the xlsx skill helper functions.
Demonstrates common workflows and use cases.
"""

from excel_helper import (
    create_workbook,
    apply_formatting,
    add_formula,
    add_chart,
    format_as_currency,
    auto_fit_columns,
    add_color_scale,
    create_sales_report_template
)


def example_simple_report():
    """Create a simple sales report with formulas."""
    print("Creating simple sales report...")

    # Create workbook
    wb, ws = create_workbook(
        title="Q1 Sales",
        headers=["Product", "Units Sold", "Price", "Revenue"]
    )

    # Add data
    data = [
        ["Widget A", 100, 25.50, None],
        ["Widget B", 150, 30.00, None],
        ["Widget C", 200, 22.75, None],
        ["Widget D", 175, 28.50, None]
    ]

    for row_idx, row_data in enumerate(data, start=2):
        for col_idx, value in enumerate(row_data, start=1):
            if value is not None:
                ws.cell(row=row_idx, column=col_idx, value=value)

    # Add formulas for Revenue column (Units * Price)
    for row in range(2, 6):
        ws[f'D{row}'] = f"=B{row}*C{row}"

    # Add totals row
    ws['A6'] = "Total"
    ws['B6'] = "=SUM(B2:B5)"
    ws['D6'] = "=SUM(D2:D5)"

    # Format
    apply_formatting(ws, "A6:D6", bold=True, bg_color="E7E6E6")
    format_as_currency(ws, "C2:C5")
    format_as_currency(ws, "D2:D6")

    # Auto-fit columns
    auto_fit_columns(ws)

    # Save
    wb.save("simple_report.xlsx")
    print("  Saved: simple_report.xlsx")


def example_with_charts():
    """Create a report with data visualization."""
    print("\nCreating report with charts...")

    wb, ws = create_workbook(
        title="Monthly Performance",
        headers=["Month", "Sales", "Costs", "Profit"]
    )

    # Add data
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    sales = [45000, 52000, 48000, 61000, 58000, 65000]
    costs = [30000, 32000, 31000, 38000, 36000, 40000]

    for i, month in enumerate(months, start=2):
        ws[f'A{i}'] = month
        ws[f'B{i}'] = sales[i-2]
        ws[f'C{i}'] = costs[i-2]
        ws[f'D{i}'] = f"=B{i}-C{i}"

    # Format as currency
    format_as_currency(ws, "B2:D7")

    # Add color scale to Profit column
    add_color_scale(ws, "D2:D7")

    # Add line chart
    add_chart(
        ws,
        chart_type="line",
        data_range="B1:D7",
        categories_range="A2:A7",
        title="Monthly Performance",
        x_axis_title="Month",
        y_axis_title="Amount ($)",
        position="F2"
    )

    # Auto-fit columns
    auto_fit_columns(ws)

    wb.save("report_with_charts.xlsx")
    print("  Saved: report_with_charts.xlsx")


def example_advanced_template():
    """Create an advanced sales report template."""
    print("\nCreating advanced sales template...")

    create_sales_report_template()
    print("  Saved: sales_report_template.xlsx")


def main():
    """Run all examples."""
    print("="*60)
    print("XLSX Skill - Example Usage")
    print("="*60)

    try:
        example_simple_report()
        example_with_charts()
        example_advanced_template()

        print("\n" + "="*60)
        print("All examples completed successfully!")
        print("Check the created files:")
        print("  - simple_report.xlsx")
        print("  - report_with_charts.xlsx")
        print("  - sales_report_template.xlsx")
        print("="*60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
