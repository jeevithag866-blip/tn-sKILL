import time
import requests

from app.config import settings


class GeminiDocumentGenerator:

    API_URL = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/{model}:generateContent?key={api_key}"
    )

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model

    def build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ):

        return f"""
You are LegalEase, an AI-powered legal document
generation assistant.

Generate a professional, structured and editable
legal document based on the following information.

DOCUMENT TYPE:
{document_type}

PARTIES INVOLVED:
{parties}

TERMS AND CONDITIONS:
{terms}

EFFECTIVE DATE:
{dates}

Instructions:

1. Create a professional legal document.
2. Start with a clear title.
3. Clearly identify all parties.
4. Include the effective date.
5. Organize the document into numbered sections.
6. Preserve all important user-provided terms.
7. Do not invent names, dates, amounts, addresses,
   laws or legal references.
8. If important information is missing, write:
   [TO BE COMPLETED]
9. Include relevant clauses for the selected
   document type.
10. Include termination provisions where appropriate.
11. Include confidentiality provisions where relevant.
12. Include signature sections.
13. Use professional legal language.
14. Return plain text only.
15. Do not return JSON.
16. Do not use Markdown code fences.
17. Do not explain the generation process.

End the document with:

Drafting aid only — review with a qualified
legal professional before use.

Return ONLY the completed legal document.
""".strip()

    def call_gemini(
        self,
        prompt: str,
        model: str,
    ):

        url = self.API_URL.format(
            model=model,
            api_key=self.api_key,
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            url,
            json=payload,
            timeout=120,
        )

        # Temporary Gemini capacity problem
        if response.status_code == 503:

            raise RuntimeError(
                "MODEL_BUSY"
            )

        if response.status_code == 429:

            raise RuntimeError(
                "RATE_LIMIT"
            )

        if response.status_code >= 400:

            try:
                error = response.json()

            except Exception:
                error = response.text

            raise RuntimeError(
                f"Gemini API error "
                f"{response.status_code}: {error}"
            )

        data = response.json()

        candidates = data.get(
            "candidates",
            []
        )

        if not candidates:

            raise RuntimeError(
                "Gemini returned no candidates."
            )

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        text = "".join(
            part.get("text", "")
            for part in parts
        ).strip()

        if not text:

            raise RuntimeError(
                "Gemini returned empty text."
            )

        return text

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
    ):

        if not self.api_key:

            return (
                self.generate_demo_document(
                    document_type,
                    parties,
                    terms,
                    dates,
                ),
                "demo-template",
                True,
            )

        prompt = self.build_prompt(
            document_type,
            parties,
            terms,
            dates,
        )

        # Primary + fallback models
        models = [
            self.model,
            "gemini-3.7-flash",
            "gemini-3.6-flash",
            "gemini-3.5-flash",
        ]

        # Remove duplicates
        models = list(
            dict.fromkeys(models)
        )

        errors = []

        for model in models:

            for attempt in range(3):

                try:

                    print(
                        f"Trying Gemini model: "
                        f"{model} "
                        f"(attempt {attempt + 1}/3)"
                    )

                    result = self.call_gemini(
                        prompt,
                        model,
                    )

                    return (
                        result,
                        model,
                        False,
                    )

                except RuntimeError as error:

                    error_text = str(error)

                    errors.append(
                        f"{model}: {error_text}"
                    )

                    # Retry temporary capacity issue
                    if error_text in [
                        "MODEL_BUSY",
                        "RATE_LIMIT",
                    ]:

                        if attempt < 2:

                            wait_time = (
                                3 * (attempt + 1)
                            )

                            print(
                                f"Gemini temporarily "
                                f"unavailable. "
                                f"Retrying in "
                                f"{wait_time} seconds..."
                            )

                            time.sleep(
                                wait_time
                            )

                            continue

                    break

                except Exception as error:

                    errors.append(
                        f"{model}: {error}"
                    )

                    break

        raise RuntimeError(
            "All Gemini models failed.\n"
            + "\n".join(errors)
        )

    def generate_demo_document(
        self,
        document_type,
        parties,
        terms,
        dates,
    ):

        term_list = []

        for term in terms.split(";"):

            term = term.strip()

            if term:

                term_list.append(
                    f"• {term}"
                )

        if not term_list:

            term_list.append(
                "• [TO BE COMPLETED]"
            )

        terms_text = "\n".join(
            term_list
        )

        return f"""
{document_type.upper()}

Effective Date: {dates}


PARTIES

{parties}


1. PURPOSE

This document records the principal terms and
conditions agreed between the parties.


2. TERMS AND CONDITIONS

{terms_text}


3. RESPONSIBILITIES

Each party shall perform the responsibilities
assigned to it under this agreement.


4. CONFIDENTIALITY

The parties shall maintain the confidentiality
of information exchanged under this agreement.

Specific confidentiality requirements:

[TO BE COMPLETED]


5. TERM AND TERMINATION

The agreement shall commence on:

{dates}

Termination conditions:

[TO BE COMPLETED]


6. GOVERNING LAW

[TO BE COMPLETED]


7. ENTIRE AGREEMENT

This document represents the understanding of
the parties regarding the subject matter described
above.


8. SIGNATURES


PARTY 1

Signature: ______________________

Name: ___________________________

Date: ___________________________


PARTY 2

Signature: ______________________

Name: ___________________________

Date: ___________________________


Drafting aid only — review with a qualified
legal professional before use.
""".strip()