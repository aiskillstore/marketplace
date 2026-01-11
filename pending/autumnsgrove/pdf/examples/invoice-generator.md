# Invoice Generator Example

Complete example of generating professional invoices from data.

## Basic Invoice

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_invoice(output_path, invoice_data):
    """
    Create professional invoice.

    Args:
        invoice_data: Dict with company, client, items, total
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Company header
    elements.append(Paragraph(invoice_data['company'], styles['Title']))
    elements.append(Paragraph(invoice_data['address'], styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Invoice details
    elements.append(Paragraph(f"<b>Invoice #:</b> {invoice_data['invoice_number']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {invoice_data['date']}", styles['Normal']))
    elements.append(Spacer(1, 0.2*inch))

    # Client information
    elements.append(Paragraph(f"<b>Bill To:</b>", styles['Heading3']))
    elements.append(Paragraph(invoice_data['client_name'], styles['Normal']))
    elements.append(Paragraph(invoice_data['client_address'], styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Items table
    table_data = [['Description', 'Quantity', 'Unit Price', 'Total']]
    for item in invoice_data['items']:
        table_data.append([
            item['description'],
            str(item['quantity']),
            f"${item['price']:.2f}",
            f"${item['quantity'] * item['price']:.2f}"
        ])

    # Add subtotal, tax, total
    subtotal = sum(item['quantity'] * item['price'] for item in invoice_data['items'])
    tax = subtotal * 0.08  # 8% tax
    total = subtotal + tax

    table_data.append(['', '', 'Subtotal:', f"${subtotal:.2f}"])
    table_data.append(['', '', 'Tax (8%):', f"${tax:.2f}"])
    table_data.append(['', '', 'Total:', f"${total:.2f}"])

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -3), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -4), 1, colors.black),
        ('LINEABOVE', (2, -3), (-1, -3), 2, colors.black),
        ('LINEABOVE', (2, -1), (-1, -1), 2, colors.black),
        ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))

    # Payment terms
    elements.append(Paragraph("<b>Payment Terms:</b>", styles['Heading3']))
    elements.append(Paragraph(invoice_data['payment_terms'], styles['Normal']))

    # Build PDF
    doc.build(elements)

# Usage example
invoice_data = {
    'company': 'Acme Corporation',
    'address': '123 Business St, City, State 12345',
    'invoice_number': 'INV-2025-001',
    'date': '2025-10-25',
    'client_name': 'John Smith',
    'client_address': '456 Client Ave, Town, State 67890',
    'items': [
        {'description': 'Web Design Services', 'quantity': 10, 'price': 150.00},
        {'description': 'Logo Design', 'quantity': 1, 'price': 500.00},
        {'description': 'Hosting (Annual)', 'quantity': 1, 'price': 200.00}
    ],
    'payment_terms': 'Net 30 days. Payment due within 30 days of invoice date.'
}

create_invoice("invoice_example.pdf", invoice_data)
print("Invoice created: invoice_example.pdf")
```

## Enhanced Invoice with Logo

```python
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def create_invoice_with_logo(output_path, invoice_data, logo_path=None):
    """Create invoice with company logo."""
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    elements = []
    styles = getSampleStyleSheet()

    # Add logo if provided
    if logo_path:
        logo = Image(logo_path, width=2*inch, height=1*inch)
        elements.append(logo)
        elements.append(Spacer(1, 0.2*inch))

    # Company header
    elements.append(Paragraph(invoice_data['company'], styles['Title']))
    elements.append(Paragraph(invoice_data['address'], styles['Normal']))
    elements.append(Paragraph(f"Phone: {invoice_data['phone']} | Email: {invoice_data['email']}", styles['Normal']))
    elements.append(Spacer(1, 0.5*inch))

    # Two-column layout for invoice details and client info
    details_table = Table([
        ['Invoice Number:', invoice_data['invoice_number'], 'Bill To:', invoice_data['client_name']],
        ['Date:', invoice_data['date'], 'Address:', invoice_data['client_address']],
        ['Due Date:', invoice_data['due_date'], 'Contact:', invoice_data['client_contact']]
    ], colWidths=[1.5*inch, 2*inch, 1*inch, 2.5*inch])

    details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (3, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))

    elements.append(details_table)
    elements.append(Spacer(1, 0.5*inch))

    # Items table with enhanced styling
    table_data = [['Item', 'Description', 'Qty', 'Rate', 'Amount']]
    for i, item in enumerate(invoice_data['items'], 1):
        table_data.append([
            str(i),
            item['description'],
            str(item['quantity']),
            f"${item['price']:.2f}",
            f"${item['quantity'] * item['price']:.2f}"
        ])

    # Calculations
    subtotal = sum(item['quantity'] * item['price'] for item in invoice_data['items'])
    discount = subtotal * (invoice_data.get('discount_percent', 0) / 100)
    tax = (subtotal - discount) * (invoice_data.get('tax_rate', 0.08))
    total = subtotal - discount + tax

    # Add financial summary rows
    table_data.append(['', '', '', 'Subtotal:', f"${subtotal:.2f}"])
    if discount > 0:
        table_data.append(['', '', '', f"Discount ({invoice_data['discount_percent']}%):", f"-${discount:.2f}"])
    table_data.append(['', '', '', f"Tax ({invoice_data.get('tax_rate', 0.08)*100:.0f}%):", f"${tax:.2f}"])
    table_data.append(['', '', '', 'TOTAL:', f"${total:.2f}"])

    table = Table(table_data, colWidths=[0.5*inch, 3*inch, 0.75*inch, 1.5*inch, 1.25*inch])
    table.setStyle(TableStyle([
        # Header styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 0), (-1, 0), 12),

        # Data rows
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -5), [colors.white, colors.HexColor('#E7E6E6')]),

        # Summary rows styling
        ('BACKGROUND', (0, -4), (-1, -1), colors.HexColor('#D9E2F3')),
        ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (3, -1), (-1, -1), 12),
        ('LINEABOVE', (3, -4), (-1, -4), 1, colors.black),
        ('LINEABOVE', (3, -1), (-1, -1), 2, colors.black),

        # Grid
        ('GRID', (0, 0), (-1, -5), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5*inch))

    # Footer sections
    footer_data = [
        ['<b>Payment Terms:</b>', '<b>Notes:</b>'],
        [invoice_data.get('payment_terms', 'Net 30'), invoice_data.get('notes', 'Thank you for your business!')]
    ]

    footer_table = Table(footer_data, colWidths=[3.5*inch, 3.5*inch])
    footer_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))

    elements.append(footer_table)

    # Build PDF
    doc.build(elements)

# Usage
invoice_data = {
    'company': 'Professional Services Inc.',
    'address': '789 Corporate Blvd, Suite 100\nBusiness City, ST 12345',
    'phone': '(555) 123-4567',
    'email': 'billing@professional.com',
    'invoice_number': 'INV-2025-042',
    'date': '2025-10-25',
    'due_date': '2025-11-24',
    'client_name': 'ABC Corporation',
    'client_address': '321 Client Street\nClient Town, ST 67890',
    'client_contact': 'contact@abccorp.com',
    'items': [
        {'description': 'Consulting Services - October 2025', 'quantity': 40, 'price': 175.00},
        {'description': 'Software License (Annual)', 'quantity': 5, 'price': 299.00},
        {'description': 'Training Session', 'quantity': 2, 'price': 500.00}
    ],
    'discount_percent': 10,
    'tax_rate': 0.08,
    'payment_terms': 'Payment due within 30 days\nAccepted methods: Check, ACH, Credit Card',
    'notes': 'Thank you for your continued business.\nPlease reference invoice number on payment.'
}

create_invoice_with_logo("professional_invoice.pdf", invoice_data)
print("Professional invoice created: professional_invoice.pdf")
```

## Batch Invoice Generation

```python
import pandas as pd
from pathlib import Path

def generate_invoices_from_csv(csv_path, output_dir, template_function):
    """Generate multiple invoices from CSV data."""
    # Read invoice data
    df = pd.read_csv(csv_path)

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    for _, row in df.iterrows():
        invoice_data = {
            'company': row['company'],
            'address': row['company_address'],
            'invoice_number': row['invoice_number'],
            'date': row['date'],
            'client_name': row['client_name'],
            'client_address': row['client_address'],
            'items': eval(row['items']),  # Be careful with eval in production
            'payment_terms': row['payment_terms']
        }

        output_file = output_path / f"{row['invoice_number']}.pdf"
        template_function(str(output_file), invoice_data)
        print(f"Generated: {output_file}")

# Usage
# generate_invoices_from_csv('invoices.csv', 'generated_invoices/', create_invoice)
```
