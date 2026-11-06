"""Download, audit and transform UCI line items into invoice itemsets."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import urllib.request
import zipfile
import pandas as pd
from .io import ROOT, save_json, save_csv, sha256

REQUIRED = ["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"]


def download(cfg: dict) -> Path:
    raw = ROOT / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    target = raw / "Online Retail.xlsx"
    if not target.exists():
        archive = raw / "online_retail.zip"
        req = urllib.request.Request(cfg["dataset_url"], headers={"User-Agent": "AIAA3111 research project"})
        print("Downloading public UCI dataset...", flush=True)
        with urllib.request.urlopen(req, timeout=120) as response, archive.open("wb") as dest:
            shutil.copyfileobj(response, dest)
        with zipfile.ZipFile(archive) as z:
            names = [n for n in z.namelist() if Path(n).name == "Online Retail.xlsx"]
            if len(names) != 1:
                raise ValueError("Expected exactly one Online Retail.xlsx in official archive")
            with z.open(names[0]) as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
    manifest = ROOT / "data/source_manifest.json"
    digest = sha256(target)
    if manifest.exists():
        previous = json.loads(manifest.read_text(encoding="utf-8"))
        if previous["sha256"] != digest:
            raise ValueError("Raw data checksum differs from the recorded source manifest")
    else:
        save_json({"url": cfg["dataset_url"], "landing_page": "https://archive.ics.uci.edu/dataset/352/online+retail", "doi": "10.24432/C5BW33", "license": "CC BY 4.0", "retrieved_utc": datetime.now(timezone.utc).isoformat(), "file": target.name, "bytes": target.stat().st_size, "sha256": digest}, manifest)
    return target


def clean_lines(raw: pd.DataFrame, non_product_codes: list[str]):
    missing = set(REQUIRED) - set(raw.columns)
    if missing:
        raise ValueError(f"Missing source fields: {sorted(missing)}")
    df = raw.copy()
    audit = []

    def exclude(mask, reason):
        nonlocal df
        before = len(df)
        df = df.loc[~mask].copy()
        audit.append({"step": reason, "removed_rows": before - len(df), "remaining_rows": len(df)})

    audit.append({"step": "raw", "removed_rows": 0, "remaining_rows": len(df)})
    exclude(df.duplicated(), "exact_duplicate_lines")
    for col in ["InvoiceNo", "StockCode", "Country"]:
        df[col] = df[col].astype("string").str.strip()
    df["InvoiceNo"] = df["InvoiceNo"].str.upper()
    df["StockCode"] = df["StockCode"].str.upper()
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["UnitPrice"] = pd.to_numeric(df["UnitPrice"], errors="coerce")
    invalid = df[["InvoiceNo", "StockCode", "InvoiceDate", "Quantity", "UnitPrice", "Country"]].isna().any(axis=1)
    invalid |= df["InvoiceNo"].eq("") | df["StockCode"].eq("") | df["Country"].eq("")
    exclude(invalid, "missing_required_basket_fields")
    exclude(df["InvoiceNo"].str.startswith("C"), "cancelled_invoice")
    exclude(df["Quantity"].le(0), "nonpositive_quantity")
    exclude(df["UnitPrice"].le(0), "nonpositive_price")
    exclude(df["StockCode"].isin(non_product_codes) | df["StockCode"].str.startswith("GIFT_"), "non_product_codes")
    # Invoice IDs define the observation. Do not silently split inconsistent IDs.
    consistency = df.groupby("InvoiceNo").agg(first=("InvoiceDate", "min"), last=("InvoiceDate", "max"), countries=("Country", "nunique"))
    # Audited source has 42 same-day invoices spanning one minute. Use earliest
    # timestamp, but reject cross-day or cross-country IDs rather than merge them.
    if (consistency["first"].dt.normalize().ne(consistency["last"].dt.normalize()) | consistency["countries"].gt(1)).any():
        raise ValueError("An invoice spans dates or countries; inspect before aggregating")
    return df, pd.DataFrame(audit)


def make_baskets(lines: pd.DataFrame) -> pd.DataFrame:
    grouped = lines.groupby("InvoiceNo", sort=True)
    baskets = grouped.agg(date=("InvoiceDate", "min"), country=("Country", "first"), customer_known=("CustomerID", lambda s: bool(s.notna().any())))
    baskets["items"] = grouped["StockCode"].agg(lambda s: tuple(sorted(set(s))))
    baskets["n_items"] = baskets["items"].map(len)
    baskets["month"] = baskets["date"].dt.strftime("%Y-%m")
    return baskets.reset_index()


def discovery(baskets: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    return baskets.loc[baskets["date"].ge(pd.Timestamp(cfg["discovery_start"])) & baskets["date"].lt(pd.Timestamp(cfg["discovery_end_exclusive"]))].copy()


def prepare(cfg: dict):
    target = download(cfg)
    raw = pd.read_excel(target, engine="openpyxl", dtype={"InvoiceNo": "string", "StockCode": "string"})
    profile = {"raw_rows": len(raw), "raw_columns": list(raw.columns), "missing_by_column": raw.isna().sum().to_dict(), "exact_duplicate_rows": int(raw.duplicated().sum()), "first_date": str(raw["InvoiceDate"].min()), "last_date": str(raw["InvoiceDate"].max()), "raw_distinct_invoices": int(raw["InvoiceNo"].nunique()), "raw_distinct_stock_codes": int(raw["StockCode"].nunique())}
    lines, audit = clean_lines(raw, cfg["non_product_codes"])
    baskets = make_baskets(lines)
    uk = baskets.loc[baskets["country"].eq(cfg["country"])]
    profile.update(clean_rows=len(lines), all_country_baskets=len(baskets), uk_baskets=len(uk), clean_products=int(lines["StockCode"].nunique()), clean_rows_missing_customer=int(lines["CustomerID"].isna().sum()), clean_rows_missing_description=int(lines["Description"].isna().sum()), singleton_baskets=int(baskets["n_items"].eq(1).sum()), same_day_multitime_invoices=int(lines.groupby("InvoiceNo")["InvoiceDate"].nunique().gt(1).sum()), basket_size_quantiles=baskets["n_items"].quantile([0, .5, .9, .99, 1]).to_dict())
    out = ROOT / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    baskets.to_pickle(out / "baskets.pkl")
    # Human labels use only discovery data; they never define model features.
    source_names = lines.loc[lines["InvoiceDate"].lt(pd.Timestamp(cfg["discovery_end_exclusive"])) & lines["InvoiceDate"].ge(pd.Timestamp(cfg["discovery_start"])) & lines["Country"].eq(cfg["country"])].dropna(subset=["Description"])
    names = source_names.groupby("StockCode")["Description"].agg(lambda s: str(s.mode().iloc[0]).strip())
    save_csv(names.rename("description").reset_index(), ROOT / "results/tables/product_labels.csv")
    save_csv(audit, ROOT / "results/tables/cleaning_audit.csv")
    for name, frame in [("all", baskets), ("uk", uk)]:
        monthly = frame.groupby("month").agg(orders=("InvoiceNo", "size"), mean_basket_size=("n_items", "mean"), median_basket_size=("n_items", "median"), known_customer_orders=("customer_known", "sum"))
        monthly["distinct_products"] = frame.groupby("month")["items"].agg(lambda s: len(set().union(*map(set, s))))
        save_csv(monthly.reset_index(), ROOT / f"results/tables/monthly_{name}.csv")
    unusual = lines.loc[~lines["StockCode"].str.match(r"^\d{5}[A-Z]*$")].groupby("StockCode").agg(rows=("StockCode", "size"), description=("Description", "first"))
    save_csv(unusual.reset_index(), ROOT / "results/tables/retained_unusual_codes.csv")
    save_json(profile, ROOT / "results/data_profile.json")
    print(json.dumps(profile, default=str, indent=2), flush=True)
    return baskets
