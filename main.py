from extractor import InvoiceExtractor
from repository import InvoiceRepository
from analytics import InvoiceAnalytics
from pathlib import Path

PDF_FOLDER = "./invoices"

def run_ingestion():

    extractor = InvoiceExtractor()
    repo = InvoiceRepository()

    pdf_files = list(Path(PDF_FOLDER).glob("*.pdf"))

    success = 0

    for pdf in pdf_files:
        try:
            invoice = extractor.extract_from_pdf(pdf)
            repo.add_invoice(invoice)
            success += 1

        except Exception as e:
            print(f"Erro ao processar {pdf.name}: {e}")

    print(f"\n✔ Ingestão finalizada: {success} arquivos processados\n")


def run_analytics():

    try:
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

if __name__ == "__main__":

    run_ingestion()
    run_analytics()
