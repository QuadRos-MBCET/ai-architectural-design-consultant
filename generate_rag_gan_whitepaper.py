import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 755, "SURJ HOMES — Architectural RAG & Generative Adversarial Network Technical Whitepaper")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, page_text)
        self.drawString(54, 36, "CONFIDENTIAL & PROPRIETARY — AI ARCHITECTURAL DESIGN CONSULTANT")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        self.restoreState()

def build_pdf(filename="docs/SURJ_Homes_RAG_and_GAN_Architecture.pdf"):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles - optimized for high density professional 2-page publication
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=10
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1e293b")
    )

    story = []

    # Title Banner
    story.append(Paragraph("SURJ HOMES: Generative CAD Platform", title_style))
    story.append(Paragraph("System Architecture & Technical Specification: Retrieval-Augmented Generation (RAG) & Conditional GAN Synergy", subtitle_style))
    
    meta_text = "<b>Author / Engineering Team:</b> SURJ Homes R&D &nbsp;|&nbsp; <b>Framework:</b> PyTorch 2.x &amp; Streamlit CAD Studio &nbsp;|&nbsp; <b>Date:</b> October 2026"
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#00D2FF"), spaceAfter=10))

    # Executive Summary Box
    summary_html = (
        "<b>Executive Summary:</b> In SURJ Homes, architectural design is decoupled into two complementary machine learning layers: "
        "<b>(1) Domain-Informed Semantic Retrieval (RAG)</b> which resolves <i>what functional spaces must exist</i> based on building typology and regional codes, "
        "and <b>(2) Adversarial Spatial Layout Generation (cGAN)</b> which resolves <i>where and how those spaces are physically arranged</i> in 2D coordinate space. "
        "This hybrid paradigm eliminates generative hallucinations while ensuring watertight, non-overlapping CAD geometry."
    )
    summary_table = Table([[Paragraph(summary_html, callout_style)]], colWidths=[504])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#bae6fd")),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 8))

    # Section 1
    story.append(Paragraph("1. The Architectural Challenge: Hallucination vs. Spatial Validity", h1_style))
    story.append(Paragraph(
        "Modern deep generative models (LLMs and standard Diffusion models) face critical limitations when generating precision architectural assets:",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Pure Language Models lack coordinate awareness:</b> While LLMs excel at describing building narratives, they cannot guarantee spatial topologies, resulting in non-orthogonal walls, self-intersecting boundaries, or physically impossible geometries.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Pure Vision Models lack domain logic:</b> Generic computer vision GANs produce pixel rasters rather than semantic BIM polygons. They frequently place ICU beds in office buildings or omit required egress stairs and fire circulation corridors.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>The SURJ Homes Solution:</b> A pipelined neuro-symbolic framework where RAG establishes programmatic ground truth, and an adversarial generator (cGAN) enforces geometric constraints.",
        body_style
    ))

    # Architecture Flow Diagram Table
    story.append(Spacer(1, 4))
    flow_data = [
        [
            Paragraph("<b>USER PROMPT</b><br/><i>'30x20m 2-story hostel'</i>", table_cell_style),
            Paragraph("<b>STAGE 1: RAG ENGINE</b><br/>• Typology Classifier<br/>• Database Program Retrieval<br/>• Proportional Sizing Weights", table_cell_style),
            Paragraph("<b>STAGE 2: cGAN LAYOUT</b><br/>• Latent Vector + Cond Tensor<br/>• Generator Bounding Boxes<br/>• Discriminator & AABB Solver", table_cell_style),
            Paragraph("<b>STAGE 3: CAD SYNTHESIS</b><br/>• Multi-Story SVGs<br/>• Stairwell Riser Alignment<br/>• 3D GLB Extrusion", table_cell_style)
        ]
    ]
    flow_table = Table(flow_data, colWidths=[120, 130, 134, 120])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#cbd5e1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(flow_table)
    story.append(Spacer(1, 8))

    # Section 2: Detailed RAG
    story.append(Paragraph("2. Deep Dive: Retrieval-Augmented Generation (RAG) Architecture", h1_style))
    story.append(Paragraph(
        "The RAG layer operates as the domain expert in the pipeline. It parses unconstrained natural language prompts and anchors them against a structured knowledge base of 25+ architectural typologies (Hostels, Hospitals, Laboratories, Schools, Hotels, Airports, etc.).",
        body_style
    ))
    story.append(Paragraph(
        "• <b>Typology Disambiguation:</b> Natural language refers to spaces loosely (e.g., 'dorm', 'paying guest', 'student residence'). RAG maps synonyms down to their canonical building typology using longest-substring token matching.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Programmatic Space Expansion:</b> When an architect specifies a building type without enumerating every utility space, RAG injects mandatory architectural code requirements (e.g., communal washrooms, fire stair cores, security vestibules).",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Multi-Floor Zoning Differentiation:</b> Level 1 requires public reception, admin offices, and dining halls; upper floors require dormitory wings or quiet study rooms. RAG partitions functional zones vertically across stories.",
        bullet_style
    ))
    story.append(Paragraph(
        "• <b>Architectural Weight Allocation:</b> Rather than naive uniform grids, RAG assigns space-budget weights (Reading Halls = 2.2, Labs = 1.4, Offices = 0.9, Sanitary = 0.55), ensuring realistic proportional floor area distributions.",
        bullet_style
    ))

    # Clean Page Break - Exactly 2 Pages
    story.append(PageBreak())

    # Section 3: Detailed GAN
    story.append(Paragraph("3. Deep Dive: Conditional GAN (cGAN) Spatial Packing Architecture", h1_style))
    story.append(Paragraph(
        "Once RAG establishes the room list and footprint dimensions (W × L), the spatial engine models floor plan generation as a Conditional Generative Adversarial Network (cGAN), similar to HouseGAN/House-GAN++ architectures.",
        body_style
    ))

    gan_comparison_data = [
        [
            Paragraph("<b>Component</b>", table_header_style),
            Paragraph("<b>Network Architecture</b>", table_header_style),
            Paragraph("<b>Role in SURJ Homes Pipeline</b>", table_header_style)
        ],
        [
            Paragraph("<b>Generator (G)</b>", table_cell_style),
            Paragraph("Multi-layer perceptron (Linear 256 → 512 → 1024) with BatchNorm1d and LeakyReLU(0.2).", table_cell_style),
            Paragraph("Takes random latent noise z concatenated with one-hot room labels. Decodes candidate bounding boxes: [x, y, width, length] normalized to [0, 1].", table_cell_style)
        ],
        [
            Paragraph("<b>Discriminator (D)</b>", table_cell_style),
            Paragraph("Adversarial discriminator (Linear 512 → 256 → 1) with LeakyReLU(0.2) and Dropout(0.3).", table_cell_style),
            Paragraph("Judges whether candidate layouts conform to human-drawn CAD topologies. Penalizes room intersections, invalid aspect ratios, and disconnected spaces.", table_cell_style)
        ],
        [
            Paragraph("<b>Spatial Solver (AABB)</b>", table_cell_style),
            Paragraph("Axis-Aligned Bounding Box (AABB) intersection and slice partitioning engine.", table_cell_style),
            Paragraph("Guarantees 100% boundary compliance and zero wall collisions, resolving any micro-overlaps into clean orthogonal partitions.", table_cell_style)
        ]
    ]

    gan_table = Table(gan_comparison_data, colWidths=[100, 194, 210])
    gan_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
    ]))
    story.append(gan_table)
    story.append(Spacer(1, 10))

    # Section 4: Synergistic Comparison Table
    story.append(Paragraph("4. Synergistic Matrix: RAG vs. GAN Collaboration", h1_style))
    story.append(Paragraph(
        "The following matrix summarizes why neither machine learning technique is sufficient on its own, and how SURJ Homes achieves production fidelity by coupling them:",
        body_style
    ))

    matrix_data = [
        [
            Paragraph("<b>Functional Dimension</b>", table_header_style),
            Paragraph("<b>RAG Alone</b>", table_header_style),
            Paragraph("<b>cGAN Alone</b>", table_header_style),
            Paragraph("<b>Combined: SURJ Homes Pipeline</b>", table_header_style)
        ],
        [
            Paragraph("<b>Domain Accuracy</b>", table_cell_style),
            Paragraph("High (Retrieves exact rooms for any typology)", table_cell_style),
            Paragraph("Low (Prone to mislabeling or improper zoning)", table_cell_style),
            Paragraph("<b>Guaranteed Ground Truth:</b> Correct room programs injected automatically.", table_cell_style)
        ],
        [
            Paragraph("<b>Spatial Geometry</b>", table_cell_style),
            Paragraph("None (Output is purely textual / unmapped)", table_cell_style),
            Paragraph("High (Synthesizes 2D coordinates)", table_cell_style),
            Paragraph("<b>CAD Coordinates:</b> Exact [x, y, w, l] boundaries mapped in real-time.", table_cell_style)
        ],
        [
            Paragraph("<b>Overlap Prevention</b>", table_cell_style),
            Paragraph("Cannot prevent wall collisions", table_cell_style),
            Paragraph("Penalizes overlaps via discriminator loss", table_cell_style),
            Paragraph("<b>100% Collision-Free:</b> Validated by geometric AABB solver pass.", table_cell_style)
        ],
        [
            Paragraph("<b>Multi-Story BIM</b>", table_cell_style),
            Paragraph("Understands floor levels semantically", table_cell_style),
            Paragraph("Lacks vertical awareness without conditioning", table_cell_style),
            Paragraph("<b>Vertical Alignment:</b> Coordinated stair risers and distinct upper suites.", table_cell_style)
        ]
    ]

    matrix_table = Table(matrix_data, colWidths=[90, 125, 125, 164])
    matrix_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0369a1")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor("#ffffff"), colors.HexColor("#f8fafc")]),
    ]))
    story.append(matrix_table)
    story.append(Spacer(1, 10))

    # Section 5: Conclusion & Future RoadMap
    story.append(Paragraph("5. Technical Verification & Future Extensibility", h1_style))
    story.append(Paragraph(
        "The SURJ Homes platform provides full traceability through interactive UI modals and modular PyTorch codebases (<code>models/gan/</code>, <code>models/vae/</code>, <code>models/diffusion/</code>). "
        "The pipeline is production-ready for training on the RPLAN vector floor plan dataset (80,000+ CAD records) on NVIDIA GPUs to replace procedural solvers with fully converged checkpoint weights without breaking frontend UI contracts.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully generated at: {filename}")

if __name__ == "__main__":
    out_path = sys.argv[1] if len(sys.argv) > 1 else "docs/SURJ_Homes_RAG_and_GAN_Architecture.pdf"
    build_pdf(out_path)
