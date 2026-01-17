import kagglehub
from pathlib import Path
import shutil

BASE_DIR = Path(__file__).parent

dataset_path = kagglehub.dataset_download(
    "ayoubcherguelaine/company-documents-dataset"
)

dataset_path = Path(dataset_path)

source_invoices = dataset_path / "CompanyDocuments" / "invoices"

target_invoices = BASE_DIR / "invoices"

if target_invoices.exists():
    shutil.rmtree(target_invoices)

shutil.copytree(source_invoices, target_invoices)

print("✔ Invoices copiados para:")
print(target_invoices)
