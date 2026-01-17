import pdfplumber
import re
from datetime import datetime
from invoice_etl.models import Invoice, Item


class InvoiceExtractor:
    def extract_from_pdf(self, file_path) -> Invoice:
        with pdfplumber.open(file_path) as pdf:

            full_text = "\n".join(t for page in pdf.pages if (t := page.extract_text()))

            order_id_match = re.search(
                r"Order ID\s*[:\-]?\s*(\S+)", full_text, re.IGNORECASE
            )
            customer_id_match = re.search(
                r"Customer ID\s*[:\-]?\s*(\S+)", full_text, re.IGNORECASE
            )
            date_match = re.search(
                r"Date\s*[:\-]?\s*([\d\-\/]+)", full_text, re.IGNORECASE
            )

            if not (order_id_match and customer_id_match and date_match):
                raise ValueError(f"Cabeçalho não reconhecido em {file_path}")

            date_str = date_match.group(1).replace("/", "-")
            try:
                invoice_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError(f"Formato de data inválido em {file_path}: {date_str}")

            product_table = None
            for page in pdf.pages:
                for table in page.extract_tables() or []:
                    if not table or not table[0]:
                        continue
                    header = " ".join(cell.lower() for cell in table[0] if cell)
                    if "product" in header and "quantity" in header:
                        product_table = table
                        break
                if product_table:
                    break

            if not product_table:
                raise ValueError(f"Tabela de produtos não encontrada em {file_path}")

            items = []
            for row in product_table[1:]:
                row = [c.strip() for c in row if c]

                if len(row) < 4:
                    continue

                try:
                    quantity = int(row[2].replace(",", ""))
                    unit_price = float(row[3].replace(",", "."))
                except ValueError:
                    continue

                items.append(
                    Item(
                        product_id=row[0],
                        product_name=row[1],
                        quantity=quantity,
                        unit_price=unit_price,
                    )
                )

            if not items:
                raise ValueError(f"Nenhum item válido extraído de {file_path}")

            invoice = Invoice(
                order_id=order_id_match.group(1),
                customer_id=customer_id_match.group(1),
                date=invoice_date,
                items=items,
            )

            return invoice
