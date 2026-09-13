from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

SEP = "|||"


def normalize_col(col):
    col = str(col).strip().lower()
    for ch in [" ", "-", "/", "(", ")", "%", ".", ":"]:
        col = col.replace(ch, "_")
    while "__" in col:
        col = col.replace("__", "_")
    return col.strip("_")


def _present(value):
    return pd.notna(value) and str(value).strip() != ""


def _string(value):
    return str(value)


def _sorted_unique(series):
    values = [_string(v) for v in series if _present(v)]
    return sorted(set(values), key=str.casefold)


def _map_one_to_many(df, parent, child):
    if parent not in df.columns or child not in df.columns:
        return {}

    valid = df[[parent, child]].dropna()
    out = {}

    for parent_value, group in valid.groupby(parent, sort=False):
        p = _string(parent_value)
        children = _sorted_unique(group[child])
        if p and children:
            out[p] = children

    return dict(sorted(out.items(), key=lambda kv: kv[0].casefold()))


def _map_compound_to_many(df, parents, child):
    required = list(parents) + [child]
    if not all(col in df.columns for col in required):
        return {}

    valid = df[required].dropna()
    out = {}

    for keys, group in valid.groupby(list(parents), sort=False):
        if not isinstance(keys, tuple):
            keys = (keys,)

        key_values = [_string(v) for v in keys]
        key = SEP.join(key_values)
        children = _sorted_unique(group[child])

        if all(key_values) and children:
            out[key] = children

    return dict(sorted(out.items(), key=lambda kv: kv[0].casefold()))


def load_dataset(path):
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    suffix = path.suffix.lower()

    if suffix == ".csv":
        try:
            df = pd.read_csv(path)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin-1")
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(path)
    else:
        raise ValueError("Dataset must be CSV, XLSX, or XLS.")

    df = df.copy()
    df.columns = [normalize_col(c) for c in df.columns]
    return df


def build_constraints(dataset_path):
    dataset_path = Path(dataset_path)
    df = load_dataset(dataset_path)

    required = [
        "category",
        "sub_category",
        "manager",
        "supervisor",
        "agent_name",
        "tenure_bucket",
        "agent_shift",
    ]

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(
            "Dataset is missing columns required for constrained UI: "
            + ", ".join(missing)
        )

    payload = {
        "version": 1,
        "source_dataset": dataset_path.name,
        "separator": SEP,
        "category_to_subcategories":
            _map_one_to_many(df, "category", "sub_category"),
        "manager_to_supervisors":
            _map_one_to_many(df, "manager", "supervisor"),
        "manager_supervisor_to_agents":
            _map_compound_to_many(
                df, ["manager", "supervisor"], "agent_name"
            ),
        "manager_supervisor_agent_to_tenure":
            _map_compound_to_many(
                df,
                ["manager", "supervisor", "agent_name"],
                "tenure_bucket",
            ),
        "manager_supervisor_agent_to_shift":
            _map_compound_to_many(
                df,
                ["manager", "supervisor", "agent_name"],
                "agent_shift",
            ),
    }

    if not payload["category_to_subcategories"]:
        raise ValueError(
            "No Category -> Sub-category relationships were found."
        )

    if not payload["manager_to_supervisors"]:
        raise ValueError(
            "No Manager -> Supervisor relationships were found."
        )

    return payload


def save_constraints(payload, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return output_path


def load_constraints(path):
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_dataset_candidates(base_dir):
    base_dir = Path(base_dir)
    patterns = [
        "*.csv", "*.xlsx", "*.xls",
        "data/*.csv", "data/*.xlsx", "data/*.xls",
    ]

    candidates = []
    for pattern in patterns:
        candidates.extend(base_dir.glob(pattern))

    unique = {}
    for p in candidates:
        if p.is_file():
            unique[str(p.resolve())] = p

    return sorted(unique.values(), key=lambda p: p.name.casefold())


def ensure_constraints(base_dir, filename="ui_constraints.json"):
    base_dir = Path(base_dir)
    constraint_path = base_dir / filename

    if constraint_path.exists():
        return load_constraints(constraint_path), constraint_path

    candidates = find_dataset_candidates(base_dir)

    if len(candidates) == 1:
        payload = build_constraints(candidates[0])
        save_constraints(payload, constraint_path)
        return payload, constraint_path

    if not candidates:
        raise FileNotFoundError(
            "ui_constraints.json is missing and no source dataset was found.\n\n"
            "Run:\n"
            "  python build_ui_constraints.py \"PATH_TO_TRAINING_DATASET.csv\"\n"
        )

    names = "\n - ".join(str(p) for p in candidates)
    raise RuntimeError(
        "ui_constraints.json is missing and multiple datasets were found:\n"
        f" - {names}\n\n"
        "Choose the exact training dataset:\n"
        "  python build_ui_constraints.py \"PATH_TO_CORRECT_DATASET.csv\""
    )
