# CSAT Flask  — Final Version

This package is the final Flask demo for the CSAT ANN notebook.

## Fixes included

- Category -> Sub-category dependency
- Manager -> Supervisor -> Agent dependency
- Agent -> valid Tenure Bucket / Agent Shift dependency
- Server-side validation of the same combinations
- ANN output probability is clearly separated from model test accuracy
- Final test accuracy shown as 72.12%
- Majority baseline shown as 69.40%
- Within ±1 CSAT shown as 84.95%
- Derived model-input preview after prediction:
  - Response time
  - Order-to-issue time
  - Survey delay
  - Issue day
  - Issue time bucket
  - Remark word count
- Punctuation-only customer remarks such as "." are rejected
- Valid sample-input button remains available

## Required folder structure

```text
CSAT_Flask_Demo_Final/
├── app.py
├── ui_constraints.py
├── build_ui_constraints.py
├── deployment_metrics.json
├── ui_constraints.json
├── requirements.txt
├── README.md
│
├── csat_artifacts/
│   ├── csat_ann.keras
│   ├── preprocessor.pkl
│   ├── label_encoder.pkl
│   ├── feature_config.json
│   └── decision_config.json
│
└── templates/
    └── index.html
```

## Step 1 — Copy model artifacts

Copy the complete `csat_artifacts` folder created by the successful notebook.

## Step 2 — Create UI constraints once

Use the SAME original dataset used by the notebook:

```powershell
python build_ui_constraints.py "eCommerce_Customer_support_data.csv"
```

This creates:

```text
ui_constraints.json
```

After this JSON exists, the raw CSV does not need to remain inside the Flask project.

If your previous constrained version already has a correct `ui_constraints.json`,
you may copy that file directly instead of rebuilding it.

## Step 3 — Run

```powershell
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Important interpretation

The result contains two different concepts:

- **ANN output probability**: the ANN's relative preference among CSAT classes
  for the submitted input.
- **Final test accuracy (72.12%)**: measured overall performance on the held-out
  test dataset.

Do not describe a 98% ANN output probability as "98% model accuracy."
