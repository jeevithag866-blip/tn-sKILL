from app.exporters.common import sanitize_text


def create_txt(text: str) -> bytes:

    clean_text = sanitize_text(text)

    return clean_text.encode(
        "utf-8"
    )