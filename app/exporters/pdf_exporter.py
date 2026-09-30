from io import BytesIO
from pathlib import Path
import tempfile

from fpdf import FPDF
from PIL import Image

from app.config import BASE_DIR
from app.exporters.common import sanitize_text


LOGO_PATH = BASE_DIR / "assets" / "legalease_logo.png"


def _prepare_logo():
    """
    Validate the LegalEase logo and create a temporary
    standard PNG file that FPDF can safely read.
    """

    if not LOGO_PATH.exists():
        print(f"PDF logo not found: {LOGO_PATH}")
        return None

    try:
        # First validate the image
        with Image.open(LOGO_PATH) as image:
            image.verify()

        # Reopen and convert to a standard RGB PNG
        with Image.open(LOGO_PATH) as image:
            image = image.convert("RGB")

            temp_file = tempfile.NamedTemporaryFile(
                suffix=".png",
                delete=False
            )

            temp_path = Path(temp_file.name)
            temp_file.close()

            image.save(temp_path, format="PNG")

            print(f"PDF logo prepared: {temp_path}")

            return str(temp_path)

    except Exception as error:
        print(f"Invalid PDF logo. PDF will be generated without logo.")
        print(f"Logo error: {error}")
        return None


class LegalEasePDF(FPDF):

    def __init__(self, logo_path=None):
        super().__init__()

        self.logo_path = logo_path

        self.set_auto_page_break(
            auto=True,
            margin=20
        )

        self.set_margins(
            left=20,
            top=20,
            right=20
        )

    def header(self):

        # Add logo only if a valid logo exists
        if self.logo_path:

            try:
                self.image(
                    self.logo_path,
                    x=75,
                    y=8,
                    w=60
                )

                self.ln(30)

            except Exception as error:

                print(
                    f"Could not insert PDF logo. "
                    f"Continuing without logo: {error}"
                )

                self.ln(5)

        else:
            self.ln(5)

        # Header line
        self.set_draw_color(180, 180, 180)

        self.line(
            20,
            35,
            190,
            35
        )

        self.ln(5)

    def footer(self):

        self.set_y(-15)

        self.set_font(
            "Times",
            "",
            8
        )

        self.set_text_color(
            100,
            100,
            100
        )

        self.cell(
            0,
            10,
            "LegalEase - AI-Powered Legal Document Generator",
            align="C"
        )


def _add_title(pdf, doc_type):

    pdf.set_font(
        "Times",
        "B",
        16
    )

    pdf.set_text_color(
        0,
        0,
        0
    )

    pdf.cell(
        0,
        12,
        doc_type.upper(),
        align="C"
    )

    pdf.ln(15)


def _add_document_content(pdf, text):

    clean_text = sanitize_text(text)

    blocks = clean_text.split("\n\n")

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        lines = block.splitlines()

        first_line = lines[0].strip()

        # Detect headings
        is_heading = (
            len(first_line) < 120
            and (
                first_line[:2].isdigit()
                or first_line.upper() == first_line
                or first_line.endswith(":")
            )
        )

        if is_heading:

            pdf.set_font(
                "Times",
                "B",
                12
            )

            pdf.multi_cell(
                0,
                7,
                first_line
            )

            pdf.ln(2)

            pdf.set_font(
                "Times",
                "",
                12
            )

            for line in lines[1:]:

                line = line.strip()

                if line:

                    pdf.multi_cell(
                        0,
                        7,
                        line
                    )

                    pdf.ln(2)

        else:

            pdf.set_font(
                "Times",
                "",
                12
            )

            for line in lines:

                line = line.strip()

                if line:

                    pdf.multi_cell(
                        0,
                        7,
                        line
                    )

                    pdf.ln(2)


def _add_terms_table(pdf, terms):

    if not terms:
        return

    items = []

    for item in terms.split(";"):

        item = item.strip()

        if item:
            items.append(item)

    if not items:
        return

    pdf.ln(5)

    pdf.set_font(
        "Times",
        "B",
        12
    )

    pdf.cell(
        0,
        8,
        "Key Terms"
    )

    pdf.ln(10)

    # Table header
    pdf.set_font(
        "Times",
        "B",
        10
    )

    pdf.cell(
        15,
        8,
        "No.",
        border=1
    )

    pdf.cell(
        155,
        8,
        "Term",
        border=1
    )

    pdf.ln()

    # Table rows
    pdf.set_font(
        "Times",
        "",
        10
    )

    for index, item in enumerate(items, start=1):

        pdf.cell(
            15,
            8,
            str(index),
            border=1
        )

        pdf.multi_cell(
            155,
            8,
            item,
            border=1
        )


def create_pdf(
    text: str,
    doc_type: str,
    terms: str = ""
) -> bytes:

    # Prepare and validate logo
    logo_path = _prepare_logo()

    # Create PDF
    pdf = LegalEasePDF(
        logo_path=logo_path
    )

    pdf.add_page()

    # Title
    _add_title(
        pdf,
        doc_type
    )

    # Document content
    _add_document_content(
        pdf,
        text
    )

    # Terms table
    _add_terms_table(
        pdf,
        terms
    )

    # Disclaimer
    pdf.ln(8)

    pdf.set_font(
        "Times",
        "I",
        9
    )

    pdf.multi_cell(
        0,
        6,
        "Drafting aid only - review with a qualified legal "
        "professional before use."
    )

    # Generate PDF bytes
    output = pdf.output()

    # fpdf2 normally returns bytes
    if isinstance(output, bytes):
        return output

    # Safety conversion for older versions
    if isinstance(output, bytearray):
        return bytes(output)

    return bytes(output)