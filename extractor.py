import pdfplumber
import re
from datetime import datetime
from models import Invoice, Item


class InvoiceExtractor:

    def extract_from_pdf(self, file_path) -> Invoice:

        with pdfplumber.open(file_path) as pdf:

            full_text = "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            )

            order_id_match = re.search(r"Order ID[:\s]+(\S+)", full_text)
            customer_id_match = re.search(r"Customer ID[:\s]+(\S+)", full_text)
            date_match = re.search(r"Date[:\s]+([\d\-\/]+)", full_text)

            if not (order_id_match and customer_id_match and date_match):
                raise ValueError("Cabeçalho não reconhecido")

            invoice_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()

            tables = pdf.pages[0].extract_tables()

            if not tables:
                raise ValueError("Nenhuma tabela encontrada")

            product_table = None

            for table in tables:
                if not table or not table[0]:
                    continue
                header = " ".join(cell.lower() for cell in table[0] if cell)
                if "product" in header and "quantity" in header:
                    product_table = table
                    break

            if not product_table:
                raise ValueError("Tabela de produtos não encontrada")

            items = []

            for row in product_table[1:]:

                row = [c.strip() for c in row if c]

                if len(row) < 4:
                    continue

                try:
                    quantity = int(row[2])
                    unit_price = float(row[3])
                except Exception as e:
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
                raise ValueError("Nenhum item válido extraído")

            invoice = Invoice(
                order_id=order_id_match.group(1),
                customer_id=customer_id_match.group(1),
                date=invoice_date,
                items=items,
            )

            return invoice
