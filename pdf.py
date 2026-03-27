"""
PDF → JPG converter (sem Poppler, sem PATH)
Converte cada página de um PDF em uma imagem JPG com máxima qualidade.
- Processamento paralelo (usa todos os núcleos do processador)
- Reduz DPI automaticamente se a página ultrapassar o limite do JPEG (65500 px)

Dependência única:
    pip install pymupdf
"""

import sys
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import fitz  # PyMuPDF

# ── Configurações ──────────────────────────────────────────────────────────────

DPI          = 300   # 300 = qualidade profissional | 600 = máximo absoluto
JPEG_QUALITY = 95    # 0-100 (95 é o teto prático)
JPEG_MAX_PX  = 65500 # limite máximo do formato JPEG

# ──────────────────────────────────────────────────────────────────────────────


def _render_page(args: tuple) -> str:
    """Renderiza uma única página (executado em processo separado)."""
    pdf_path, page_index, total, digits, dest, dpi, quality = args

    doc  = fitz.open(pdf_path)
    page = doc[page_index]

    # Calcula DPI seguro para não ultrapassar o limite JPEG
    safe_dpi = dpi
    rect     = page.rect  # tamanho original em pontos (72 pt = 1 inch)
    max_dim  = max(rect.width, rect.height)
    max_dpi  = int((JPEG_MAX_PX / max_dim) * 72)

    if safe_dpi > max_dpi:
        safe_dpi = max_dpi
        note = f" (DPI reduzido para {safe_dpi} — página muito grande)"
    else:
        note = ""

    scale  = safe_dpi / 72
    matrix = fitz.Matrix(scale, scale)
    pix    = page.get_pixmap(matrix=matrix, alpha=False)

    filename = Path(dest) / f"pagina_{str(page_index + 1).zfill(digits)}.jpg"
    pix.save(str(filename), output="jpeg", jpg_quality=quality)
    doc.close()

    return f"  ✔ Página {page_index + 1}/{total} → {filename.name}{note}"


def pdf_to_jpg(pdf_path: str, output_dir: str | None = None, dpi: int = DPI) -> list[str]:
    """
    Converte cada página de um PDF em um arquivo JPG.

    Args:
        pdf_path:   Caminho do arquivo PDF de entrada.
        output_dir: Pasta de saída (padrão: subpasta com nome do PDF).
        dpi:        Resolução de renderização (padrão: 300).

    Returns:
        Lista com os caminhos dos arquivos JPG gerados.
    """
    import os

    pdf_path = Path(pdf_path).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"O arquivo precisa ter extensão .pdf: {pdf_path}")

    dest = Path(output_dir) if output_dir else pdf_path.parent / pdf_path.stem
    dest.mkdir(parents=True, exist_ok=True)

    doc    = fitz.open(str(pdf_path))
    total  = len(doc)
    digits = len(str(total))
    doc.close()

    workers = os.cpu_count() or 1

    print(f"📄 PDF      : {pdf_path}")
    print(f"📁 Saída    : {dest}")
    print(f"🖨  DPI      : {dpi}")
    print(f"🎨 Qualidade: {JPEG_QUALITY}")
    print(f"⚙️  Núcleos  : {workers}")
    print()

    args_list = [
        (str(pdf_path), i, total, digits, str(dest), dpi, JPEG_QUALITY)
        for i in range(total)
    ]

    saved: list[str] = [""] * total

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(_render_page, args): args[1] for args in args_list}
        for future in as_completed(futures):
            page_index = futures[future]
            try:
                msg = future.result()
                print(msg)
                saved[page_index] = str(dest / f"pagina_{str(page_index + 1).zfill(digits)}.jpg")
            except Exception as e:
                print(f"  ✖ Página {page_index + 1} falhou: {e}")

    print(f"\n✅ {total} imagem(ns) salva(s) em: {dest}")
    return saved


# ── Ponto de entrada ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python pdf_to_jpg.py <arquivo.pdf> [pasta_de_saida] [dpi]")
        print("Exemplo: python pdf_to_jpg.py relatorio.pdf ./imagens 300")
        sys.exit(1)

    pdf_arg = sys.argv[1]
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None
    dpi_arg = int(sys.argv[3]) if len(sys.argv) > 3 else DPI

    pdf_to_jpg(pdf_arg, out_arg, dpi_arg)
