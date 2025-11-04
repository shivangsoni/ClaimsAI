"""
PDF Converter for Test Claims
Converts text files to PDF format for easier document handling
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    import os
except ImportError:
    print("Error: reportlab library not installed. Please run: pip install reportlab")
    exit(1)

def text_to_pdf(input_file, output_file):
    """Convert text file to formatted PDF"""
    
    # Create PDF document
    doc = SimpleDocTemplate(output_file, pagesize=letter,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get default styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor='darkblue',
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6,
        leftIndent=20
    )
    
    # Read input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Build document content
    story = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        
        if not line:  # Empty line
            story.append(Spacer(1, 6))
            continue
            
        if line == "INSURANCE CLAIM FORM":
            story.append(Paragraph(line, title_style))
        elif line.endswith(':') and len(line.split()) <= 3:  # Section headers
            story.append(Paragraph(line, header_style))
        elif line.startswith('✓') or line.startswith('✗'):  # Checkmarks
            story.append(Paragraph(line, body_style))
        elif line.startswith('RED FLAGS') or line.startswith('DECLARATION'):
            story.append(Paragraph(line, header_style))
        else:
            # Regular text
            story.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(story)
    print(f"✓ Created PDF: {output_file}")

def main():
    """Convert both test claim files to PDF"""
    
    test_claims_dir = "test-claims"
    
    # Check if directory exists
    if not os.path.exists(test_claims_dir):
        print(f"Error: {test_claims_dir} directory not found")
        return
    
    # Convert files
    files_to_convert = [
        ("valid_claim_example.txt", "valid_claim_example.pdf"),
        ("invalid_claim_example.txt", "invalid_claim_example.pdf")
    ]
    
    for input_file, output_file in files_to_convert:
        input_path = os.path.join(test_claims_dir, input_file)
        output_path = os.path.join(test_claims_dir, output_file)
        
        if os.path.exists(input_path):
            try:
                text_to_pdf(input_path, output_path)
            except Exception as e:
                print(f"Error converting {input_file}: {e}")
        else:
            print(f"Warning: {input_path} not found")
    
    print("\nPDF conversion completed!")
    print("You can now upload PDF files through the ClaimsAI interface.")

if __name__ == "__main__":
    main()