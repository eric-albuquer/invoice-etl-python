import json
from pathlib import Path


class InvoiceRepository:
    def __init__(self, db_path="database.json"):
        self.db_path = Path(db_path)
        self.data, self._order_ids = self._load()
        self._buffer = []

    def _load(self):
        if not self.db_path.exists():
            return [], set()

        try:
            with open(self.db_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

                if not content:
                    return [], set()

                data = json.loads(content)
                order_ids = {inv["order_id"] for inv in data}

                return data, order_ids

        except json.JSONDecodeError:
            print("⚠ database.json inválido. Recriando...")
            return [], set()

    def _save(self):
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def exists(self, order_id: str) -> bool:
        return order_id in self._order_ids

    def add_invoice(self, invoice):
        if self.exists(invoice.order_id):
            print(f"⚠ Invoice {invoice.order_id} já existe.")
            return

        self._buffer.append(invoice.model_dump(mode="json"))
        self._order_ids.add(invoice.order_id)

        print(f"✔ Invoice {invoice.order_id} adicionada ao buffer.")

    def flush(self):
        """Grava todas as invoices do buffer no database.json"""
        if not self._buffer:
            return
        self.data.extend(self._buffer)
        self._save()
        print(f"✔ {len(self._buffer)} invoices salvas no database.json")
        self._buffer.clear()
