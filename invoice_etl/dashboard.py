import matplotlib.pyplot as plt


class Dashboard:
    def __init__(self, analytics):
        self.analytics = analytics

    def run(self):
        self.show_top_products()
        self.show_price_distribution()
        self.show_invoice_value_distribution()
        self.show_top_customers()
        self.show_quantity_per_product()

    def show_top_products(self, top_n=10):
        total_per_product = self.analytics.total_spent_per_product()
        top_products = total_per_product.sort_values(ascending=False).head(top_n)
        plt.figure(figsize=(10, 6))
        top_products.plot(kind="bar", color="skyblue")
        plt.title(f"Top {top_n} Produtos por Total Gasto")
        plt.ylabel("Total Gasto")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_price_distribution(self):
        df = self.analytics.product_price_list()
        plt.figure(figsize=(10, 6))
        plt.hist(df["unit_price"], bins=20, color="lightgreen", edgecolor="black")
        plt.title("Distribuição de Preços Unitários")
        plt.xlabel("Preço Unitário")
        plt.ylabel("Quantidade de Produtos")
        plt.show()

    def show_invoice_value_distribution(self):
        totals = self.analytics.get_all_invoice_totals()
        plt.figure(figsize=(10, 6))
        plt.hist(totals, bins=20, color="orange", edgecolor="black")
        plt.title("Distribuição dos Valores das Faturas")
        plt.xlabel("Valor da Fatura")
        plt.ylabel("Quantidade")
        plt.show()

    def show_top_customers(self, top_n=10):
        totals_per_customer = self.analytics.get_total_per_customer()
        top_customers = totals_per_customer.sort_values(ascending=False).head(top_n)
        plt.figure(figsize=(10, 6))
        top_customers.plot(kind="bar", color="purple")
        plt.title(f"Top {top_n} Clientes por Faturamento")
        plt.ylabel("Total Gasto")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def show_quantity_per_product(self, top_n=10):
        quantities = self.analytics.get_quantity_per_product()
        top_products = quantities.sort_values(ascending=False).head(top_n)
        plt.figure(figsize=(10, 6))
        top_products.plot(kind="bar", color="teal")
        plt.title(f"Top {top_n} Produtos por Quantidade Vendida")
        plt.ylabel("Quantidade Vendida")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
