# app/db/init_seed.py

from __future__ import annotations

import random
from datetime import datetime
from uuid import uuid4
from typing import Any, Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.db.models import Dataset, Record, DatasetField, Bookmark


# --------- Helpers for stats --------- #

def infer_type(value: Any) -> str:
    """Very simple type inference just for demos."""
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    # could add datetime parsing here if you want
    return "string"


def compute_schema_stats_for_dataset(
    db: Session,
    dataset: Dataset,
) -> None:
    """
    Scan all records for a dataset and populate dataset_fields
    + update datasets.row_count.

    This is done in Python because our demo datasets are small (a few thousand rows),
    and it's easier to understand than fancy SQL.
    """
    records: List[Record] = db.scalars(
        select(Record).where(Record.dataset_id == dataset.id)
    ).all()

    row_count = len(records)
    dataset.row_count = row_count
    dataset.updated_at = datetime.utcnow()

    # Clear old stats for this dataset (so you can re-run the script)
    db.query(DatasetField).filter(
        DatasetField.dataset_id == dataset.id
    ).delete()

    if row_count == 0:
        return

    # Collect all field names we see in any payload
    field_names: set[str] = set()
    for rec in records:
        if isinstance(rec.payload, dict):
            field_names.update(rec.payload.keys())

    for field_name in sorted(field_names):
        values: List[Any] = [
            (rec.payload or {}).get(field_name) for rec in records
        ]
        non_null_values = [v for v in values if v is not None]

        null_frac = 1.0 - (len(non_null_values) / row_count)
        distinct_count = len(set(non_null_values))
        example_value = non_null_values[0] if non_null_values else None

        # infer a "type" based on first non-null
        value_type = infer_type(example_value)

        df = DatasetField(
            dataset_id=dataset.id,
            name=field_name,
            type=value_type,
            null_frac=float(null_frac),
            distinct_count=distinct_count,
            example_value=example_value,
        )
        db.add(df)


# --------- Data generation helpers --------- #

def random_gene_payload() -> Dict[str, Any]:
    symbol = random.choice(["TP53", "BRCA1", "EGFR", "MYC", "KRAS"])
    ensembl_id = f"ENSG{random.randint(1000000000, 9999999999)}"
    length = random.randint(500, 20000)
    gc_content = round(random.uniform(0.3, 0.7), 2)
    is_protein_coding = random.choice([True, False])

    return {
        "symbol": symbol,
        "ensembl_id": ensembl_id,
        "length": length,
        "gc_content": gc_content,
        "is_protein_coding": is_protein_coding,
    }


def random_assay_payload() -> Dict[str, Any]:
    platform = random.choice(["Illumina", "Nanopore", "PacBio"])
    name = random.choice(["RNA-seq", "WGS", "ChIP-seq", "ATAC-seq"])
    read_length = random.choice([75, 100, 150, 250])
    coverage = round(random.uniform(10, 100), 1)
    date = datetime(
        year=random.randint(2018, 2025),
        month=random.randint(1, 12),
        day=random.randint(1, 28),
    ).date().isoformat()

    return {
        "name": name,
        "platform": platform,
        "read_length": read_length,
        "coverage": coverage,
        "date": date,
    }


def random_experiment_payload() -> Dict[str, Any]:
    condition = random.choice(["control", "treated", "knockout"])
    gene_symbol = random.choice(["TP53", "BRCA1", "EGFR", "MYC", "KRAS"])
    value = round(random.uniform(-2.0, 2.0), 3)
    pvalue = round(10 ** random.uniform(-6, -1), 6)
    date = datetime(
        year=random.randint(2018, 2025),
        month=random.randint(1, 12),
        day=random.randint(1, 28),
    ).date().isoformat()

    return {
        "gene_symbol": gene_symbol,
        "condition": condition,
        "value": value,
        "pvalue": pvalue,
        "date": date,
    }


def seed_dataset(
    db: Session,
    name: str,
    description: str,
    n_rows: int,
    payload_fn,
) -> Dataset:
    """
    Create a dataset, insert n_rows records using payload_fn, and compute stats.
    """
    dataset = Dataset(
        id=uuid4(),
        name=name,
        description=description,
    )
    db.add(dataset)
    db.flush()  # get dataset.id

    for _ in range(n_rows):
        rec = Record(
            dataset_id=dataset.id,
            payload=payload_fn(),
        )
        db.add(rec)

    # Flush records so stats can see them
    db.flush()

    compute_schema_stats_for_dataset(db, dataset)

    return dataset


def reset_demo_data(db: Session) -> None:
    """
    Wipe existing demo data so the script is idempotent for development.
    """
    db.query(Bookmark).delete()
    db.query(DatasetField).delete()
    db.query(Record).delete()
    db.query(Dataset).delete()
    db.commit()


def main() -> None:
    db: Session = SessionLocal()
    try:
        print("Clearing existing demo data...")
        reset_demo_data(db)

        print("Seeding genes dataset...")
        seed_dataset(
            db,
            name="genes",
            description="Human genes",
            n_rows=3000,
            payload_fn=random_gene_payload,
        )

        print("Seeding assays dataset...")
        seed_dataset(
            db,
            name="assays",
            description="Sequencing assays",
            n_rows=2000,
            payload_fn=random_assay_payload,
        )

        print("Seeding experiments dataset...")
        seed_dataset(
            db,
            name="experiments",
            description="Gene expression experiments",
            n_rows=2500,
            payload_fn=random_experiment_payload,
        )

        db.commit()
        print("Done.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
