
from langchain_core.tools import tool
from datetime import datetime
from pathlib import Path
import subprocess
import shutil
import re


@tool
def render_latex_pdf(latex_content: str) -> str:
    """Compile a LaTeX document into a PDF using Tectonic."""

    # Locate Tectonic in PATH or beside this Python file.
    tectonic_path = shutil.which("tectonic")

    if tectonic_path is None:
        local_tectonic = Path(__file__).resolve().parent / "tectonic.exe"

        if local_tectonic.is_file():
            tectonic_path = str(local_tectonic)
        else:
            raise RuntimeError(
                "Tectonic not found. Make sure tectonic.exe is in "
                "the project folder or available in PATH."
            )

    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tex_file = output_dir / f"paper_{timestamp}.tex"
    pdf_file = output_dir / f"paper_{timestamp}.pdf"

    try:
        # Repair the specific malformed table command seen in your log.
        latex_content = re.sub(
            r"\\bottom\s*>",
            r"\\bottomrule",
            latex_content,
        )

        tex_file.write_text(latex_content, encoding="utf-8")

        result = subprocess.run(
            [
                tectonic_path,
                "--keep-logs",
                "--keep-intermediates",
                "--outdir",
                str(output_dir),
                str(tex_file),
            ],
            cwd=str(output_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

        if result.returncode != 0:
            details = result.stderr or result.stdout or "Unknown error"
            raise RuntimeError(
                f"Tectonic compilation failed:\n{details}\n\n"
                f"LaTeX source saved at: {tex_file}"
            )

        if not pdf_file.exists():
            raise FileNotFoundError(
                f"PDF was not generated. Expected: {pdf_file}"
            )

        print(f"PDF generated successfully: {pdf_file}")
        return str(pdf_file)

    except Exception as exc:
        print(f"Error rendering LaTeX: {exc}")
        raise
