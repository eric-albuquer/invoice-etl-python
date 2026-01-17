import kagglehub
from pathlib import Path
import shutil


def download_invoices(target_folder=None):
    BASE_DIR = Path(__file__).parent
    target_invoices = Path(target_folder) if target_folder else BASE_DIR / "invoices"

    dataset_path = kagglehub.dataset_download(
        "ayoubcherguelaine/company-documents-dataset"
    )
    dataset_path = Path(dataset_path)

    source_invoices = dataset_path / "CompanyDocuments" / "invoices"

    if target_invoices.exists():
        shutil.rmtree(target_invoices)

    shutil.copytree(source_invoices, target_invoices)
    print("✔ Invoices copiados para:", target_invoices)

    return target_invoices
