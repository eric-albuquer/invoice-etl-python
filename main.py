from pathlib import Path
from invoice_etl.repository import InvoiceRepository
from math import ceil
from multiprocessing import Pool, cpu_count
from invoice_etl.download_dataset import download_invoices
import sys
import time
import logging
from logging.handlers import RotatingFileHandler
import multiprocessing
from datetime import datetime

PDF_FOLDER = Path("./invoices")

# =============================
# CONFIGURAÇÃO DE LOG
# =============================

LOG_FILE = "ingestion.log"

handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5_000_000,
    backupCount=5,
    encoding="utf-8"
)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | PID:%(process)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

handler.setFormatter(formatter)

logger = logging.getLogger("ingestion")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

# =============================
# FUNÇÕES DE INGESTÃO (PARALELO)
# =============================

def process_batch(pdf_paths):
    from invoice_etl.extractor import InvoiceExtractor

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


def run_ingestion_parallel():
    logger.info("Ingestão paralela iniciada")

    repo = InvoiceRepository()
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
        pdf_files[i:i + batch_size]
        for i in range(0, len(pdf_files), batch_size)
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

    repo.flush()

    print(f"\n✔ Ingestão finalizada: {success} arquivos processados")

    if errors:
        print(f"⚠ {errors} PDFs não processados. Veja ingestion.log")

    logger.info(
        f"Ingestão paralela finalizada | Sucesso={success} | Erros={errors}"
    )


# =============================
# INGESTÃO SEQUENCIAL
# =============================

def run_ingestion():
    logger.info("Ingestão sequencial iniciada")

    repo = InvoiceRepository()
    pdf_files = list(PDF_FOLDER.glob("*.pdf"))

    if not pdf_files:
        print("Nenhum PDF encontrado na pasta.")
        logger.warning("Nenhum PDF encontrado para ingestão")
        return

    success = 0
    errors = 0

    from invoice_etl.extractor import InvoiceExtractor
    extractor = InvoiceExtractor()

    for pdf_path in pdf_files:
        try:
            invoice = extractor.extract_from_pdf(pdf_path)
            repo.add_invoice(invoice)
            success += 1

        except Exception:
            logger.exception(f"Erro ao processar: {pdf_path.name}")
            errors += 1

    repo.flush()

    print(f"\n✔ Ingestão finalizada: {success} arquivos processados")

    if errors:
        print(f"⚠ {errors} PDFs não processados. Veja ingestion.log")

    logger.info(
        f"Ingestão sequencial finalizada | Sucesso={success} | Erros={errors}"
    )


# =============================
# ANALYTICS
# =============================

def run_analytics():
    try:
        from invoice_etl.analytics import InvoiceAnalytics

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

        logger.info("Analytics executado com sucesso")

    except Exception:
        logger.exception("Erro ao executar analytics")
        print("Analytics não executado. Veja ingestion.log")


# =============================
# MAIN
# =============================

if __name__ == "__main__":
    multiprocessing.freeze_support()

    start_time = time.time()

    logger.info("=" * 70)
    logger.info(f"NOVA EXECUÇÃO — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)

    logger.info("Pipeline iniciado")

    if not PDF_FOLDER.exists():
        print("Pasta 'invoices' não encontrada. Baixando dataset...")
        logger.info("Dataset não encontrado. Iniciando download.")
        download_invoices(PDF_FOLDER)

    use_parallel = "--parallel" in sys.argv

    if use_parallel:
        run_ingestion_parallel()
    else:
        run_ingestion()

    run_analytics()

    elapsed = time.time() - start_time

    print(f"\n⏱ Tempo total: {elapsed:.2f}s")
    logger.info(f"Pipeline finalizado | Tempo total: {elapsed:.2f}s")