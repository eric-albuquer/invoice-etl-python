from pathlib import Path
from repository import InvoiceRepository
from math import ceil
from multiprocessing import Pool, cpu_count
from download_dataset import download_invoices
import sys

PDF_FOLDER = Path("./invoices")


# ----------------------------
# Funções de ingestão (paralelo)
# ----------------------------
def process_batch(pdf_paths):
    from extractor import InvoiceExtractor

    extractor = InvoiceExtractor()
    invoices = []
    errors = []
    for pdf_path in pdf_paths:
        try:
            invoice = extractor.extract_from_pdf(pdf_path)
            invoices.append(invoice)
        except Exception as e:
            errors.append(f"{pdf_path.name}: {e}")
    return invoices, errors


def run_ingestion_parallel():
    repo = InvoiceRepository()
    pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))

    if not pdf_files:
        print("Nenhum PDF encontrado na pasta.")
        return

    success = 0
    errors = []

    n_processes = cpu_count()
    batch_size = ceil(len(pdf_files) / n_processes)
    batches = [
        pdf_files[i : i + batch_size] for i in range(0, len(pdf_files), batch_size)
    ]

    from multiprocessing import Pool

    with Pool(processes=n_processes) as pool:
        results = pool.map(process_batch, batches)

    for invoices, errs in results:
        for invoice in invoices:
            repo.add_invoice(invoice)
            success += 1
        for err in errs:
            errors.append(err)
            print(f"Erro: {err}")

    repo.flush()
    print(f"\n✔ Ingestão finalizada: {success} arquivos processados")
    if errors:
        print(f"⚠ {len(errors)} PDFs não processados devido a erros.\n")


# ================================
# Função que processa PDFs sequencialmente
# ================================
def run_ingestion():
    repo = InvoiceRepository()
    pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))

    if not pdf_files:
        print("Nenhum PDF encontrado na pasta.")
        return

    success = 0
    errors = []

    for pdf_path in pdf_files:
        try:
            from extractor import InvoiceExtractor

            extractor = InvoiceExtractor()

            invoice = extractor.extract_from_pdf(pdf_path)
            repo.add_invoice(invoice)
            success += 1

        except Exception as e:
            errors.append(f"{pdf_path.name}: {e}")
            print(f"Erro: {pdf_path.name}: {e}")

    # Grava todas as invoices de uma vez
    repo.flush()
    print(f"\n✔ Ingestão finalizada: {success} arquivos processados")
    if errors:
        print(f"⚠ {len(errors)} PDFs não processados devido a erros.\n")


# ----------------------------
# Função de analytics console
# ----------------------------
def run_analytics():
    try:
        from analytics import InvoiceAnalytics

        analytics = InvoiceAnalytics()

        print("\n===== ANALYTICS =====")
        print("Média valor das faturas:")
        print(analytics.average_invoice_value())

        print("\nProduto mais comprado:")
        print(analytics.most_frequent_product())

        print("\nTotal gasto por produto:")
        print(analytics.total_spent_per_product())

        print("\nLista produtos e preços:")
        print(analytics.product_price_list())

    except Exception as e:
        print(f"Analytics não executado: {e}")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":

    if not PDF_FOLDER.exists():
        print("Pasta 'invoices' não encontrada. Baixando dataset...")
        download_invoices(PDF_FOLDER)

    use_parallel = "--parallel" in sys.argv

    if use_parallel:
        run_ingestion_parallel()
    else:
        run_ingestion()

    run_analytics()