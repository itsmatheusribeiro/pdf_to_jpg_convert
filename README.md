# 📄 PDF to JPG Converter

Converte cada página de um PDF em uma imagem JPG com máxima qualidade.

- ✅ Sem dependências externas (não precisa do Poppler)
- ⚡ Processamento paralelo (usa todos os núcleos do processador)
- 🛡️ Reduz DPI automaticamente em páginas muito grandes (evita erro de limite JPEG)

---

## Instalação

Você precisa ter o [Python](https://www.python.org/downloads/) instalado. Depois, instale a única dependência:

```bash
pip install pymupdf
```

---

## Uso

```bash
python pdf_to_jpg.py <arquivo.pdf> [pasta_de_saida] [dpi]
```

### Exemplos

```bash
# Básico — cria uma subpasta com o nome do PDF
python pdf_to_jpg.py relatorio.pdf

# Com pasta de saída personalizada
python pdf_to_jpg.py relatorio.pdf ./imagens

# Com DPI customizado
python pdf_to_jpg.py relatorio.pdf ./imagens 600
```

---

## Parâmetros

| Parâmetro | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `arquivo.pdf` | ✅ | — | Caminho do PDF de entrada |
| `pasta_de_saida` | ❌ | Subpasta com nome do PDF | Onde as imagens serão salvas |
| `dpi` | ❌ | `300` | Resolução da imagem (300 = profissional, 600 = máximo) |

---

## Saída

As imagens são salvas com nomes sequenciais:

```
relatorio/
├── pagina_01.jpg
├── pagina_02.jpg
└── pagina_03.jpg
```

---

## Requisitos

- Python 3.10+
- [PyMuPDF](https://pymupdf.readthedocs.io/) (`pip install pymupdf`)
