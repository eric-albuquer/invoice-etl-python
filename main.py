from invoice_etl.repository import InvoiceRepository
import logging
from logging.handlers import RotatingFileHandler
from invoice_etl.extractor import InvoiceExtractor
from multiprocessing import Pool, cpu_count, freeze_support
from pathlib import Path
from math import ceil

# =============================
# PASTA COM PDF(s)
# =============================

PDF_FOLDER = Path("./invoices")

# =============================
# CONFIGURAÇÃO DE LOG
# =============================

LOG_FILE = Path("ingestion.log")

handler = RotatingFileHandler(
    LOG_FILE, maxBytes=5_000_000, backupCount=5, encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | PID:%(process)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

handler.setFormatter(formatter)

logger = logging.getLogger("ingestion")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# =============================
# FUNÇÕES DE INGESTÃO (PARALELO)
# =============================

def process_batch(pdf_paths):
    extractor = InvoiceExtractor()
    invoices = []
    errors = []

    for pdf_path in pdf_paths:
        try:
            invoice = extractor.extract_from_pdf(pdf_path)
            invoices.append(invoice)

        except Exception:
            error_msg = f"{pdf_path.name}"
            errors.append(error_msg)

    return invoices, errors


def run_ingestion_parallel(repo: InvoiceRepository):
    logger.info("Ingestão paralela iniciada")

    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("Nenhum PDF encontrado na pasta.")
        logger.warning("Nenhum PDF encontrado para ingestão")
        return

    success = 0
    errors = 0

    n_processes = max(1, cpu_count())
    batch_size = ceil(len(pdf_files) / n_processes)

    batches = [
        pdf_files[i : i + batch_size] for i in range(0, len(pdf_files), batch_size)
    ]

    with Pool(processes=n_processes) as pool:
        results = pool.map(process_batch, batches)

    for invoices, errs in results:
        for invoice in invoices:
            repo.add_invoice(invoice)
            success += 1

        errors += len(errs)

        for err in errs:
            logger.exception(f"Erro ao processar: {err}")

    print(f"\n✔ Ingestão finalizada: {success} arquivos processados")

    if errors:
        print(f"⚠ {errors} PDFs não processados. Veja ingestion.log")

    logger.info(f"Ingestão paralela finalizada | Sucesso={success} | Erros={errors}")

# =============================
# INGESTÃO SEQUENCIAL
# =============================

def run_ingestion(repo: InvoiceRepository):
    logger.info("Ingestão sequencial iniciada")

    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("Nenhum PDF encontrado na pasta.")
        logger.warning("Nenhum PDF encontrado para ingestão")
        return

    success = 0
    errors = 0

    extractor = InvoiceExtractor()

    for pdf_path in pdf_files:
        try:
            invoice = extractor.extract_from_pdf(pdf_path)
            repo.add_invoice(invoice)
            success += 1

        except Exception:
            logger.exception(f"Erro ao processar: {pdf_path.name}")
            errors += 1

    print(f"\n✔ Ingestão finalizada: {success} arquivos processados")

    if errors:
        print(f"⚠ {errors} PDFs não processados. Veja ingestion.log")

    logger.info(f"Ingestão sequencial finalizada | Sucesso={success} | Erros={errors}")

# =============================
# MAIN
# =============================

def main():
    from invoice_etl.download_dataset import download_invoices
    from invoice_etl.dashboard import Dashboard
    from invoice_etl.analytics import InvoiceAnalytics
    from datetime import datetime
    from sys import argv
    import time

    freeze_support()

    start_time = time.time()

    logger.info("=" * 70)
    logger.info(f"NOVA EXECUÇÃO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    logger.info("Pipeline iniciado")

    if not PDF_FOLDER.exists():
        print("Pasta 'invoices' não encontrada. Baixando dataset...")
        logger.info("Dataset não encontrado. Iniciando download.")
        download_invoices(PDF_FOLDER)

    use_parallel = "--parallel" in argv
    show_dashboard = "--dashboard" in argv

    repo = InvoiceRepository()

    if use_parallel:
        run_ingestion_parallel(repo)
    else:
        run_ingestion(repo)

    repo.flush()

    analytics = InvoiceAnalytics()

    analytics.run()

    elapsed = time.time() - start_time

    if show_dashboard:
        dashboard = Dashboard(analytics)
        dashboard.run()

    print(f"\n⏱ Tempo total: {elapsed:.2f}s")
    logger.info(f"Pipeline finalizado | Tempo total: {elapsed:.2f}s")


if __name__ == "__main__":
    main()