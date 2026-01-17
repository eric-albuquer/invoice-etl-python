import json
from pathlib import Path
from models import Invoice


class InvoiceRepository:

    def __init__(self, db_path="database.json"):
        self.db_path = Path(db_path)
        self.data = self._load()

    def _load(self):

        if not self.db_path.exists():
            return []

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if not content:
                    return []

                return json.loads(content)

        except json.JSONDecodeError:
            print("⚠ database.json inválido. Recriando...")
            return []

    def _save(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def exists(self, order_id: str) -> bool:
        return any(inv["order_id"] == order_id for inv in self.data)

    def add_invoice(self, invoice: Invoice):

        if self.exists(invoice.order_id):
            print(f"⚠ Invoice {invoice.order_id} já existe.")
            return

        self.data.append(invoice.model_dump(mode="json"))

        self._save()
        print(f"✔ Invoice {invoice.order_id} salva.")
