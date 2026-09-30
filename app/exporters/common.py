import re


def sanitize_text(text: str) -> str:

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u00a0": " ",
        "\u2022": "•",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    # Remove control characters.
    text = re.sub(
        r"[\x00-\x08\x0b\x0c\x0e-\x1f]",
        "",
        text,
    )

    return text.strip()