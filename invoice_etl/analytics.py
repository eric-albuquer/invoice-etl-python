from pathlib import Path
import pandas as pd


class InvoiceAnalytics:
    def __init__(self, invoices=None, db_path="database.json"):

        if invoices is not None:
            df = pd.DataFrame(invoices)
        else:
            if not Path(db_path).exists():
                raise FileNotFoundError(f"{db_path} não existe")
            df = pd.read_json(db_path)

        if df.empty:
            raise ValueError("Sem dados para análise")

        self.df = df
        self.items_df = self.df.explode("items")
        self.items_df = pd.concat(
            [
                self.items_df.drop(columns=["items"]),
                self.items_df["items"].apply(pd.Series),
            ],
            axis=1,
        )
        self.items_df["total"] = self.items_df["quantity"] * self.items_df["unit_price"]

    def average_invoice_value(self):
        invoice_totals = self.items_df.groupby("order_id")["total"].sum()
        return invoice_totals.mean()

    def most_frequent_product(self):
        return self.items_df["product_name"].value_counts().idxmax()

    def total_spent_per_product(self):
        return (
            self.items_df.groupby("product_name")["total"]
            .sum()
            .sort_values(ascending=False)
        )

    def product_price_list(self):
        return (
            self.items_df[["product_name", "unit_price"]]
            .drop_duplicates()
            .sort_values("product_name")
        )

    def get_all_invoice_totals(self):
        return self.items_df.groupby("order_id")["total"].sum()

    def get_total_per_customer(self):
        return (
            self.items_df.groupby("customer_id")["total"]
            .sum()
            .sort_values(ascending=False)
        )

    def get_quantity_per_product(self):
        return (
            self.items_df.groupby("product_name")["quantity"]
            .sum()
            .sort_values(ascending=False)
        )

    def run(self):
        print("\n===== ANALYTICS =====")
        print("Média valor das faturas:")
        print(self.average_invoice_value())
        print("\nProduto mais comprado:")
        print(self.most_frequent_product())
        print("\nTotal gasto por produto:")
        print(self.total_spent_per_product())
        print("\nLista produtos e preços:")
        print(self.product_price_list())
