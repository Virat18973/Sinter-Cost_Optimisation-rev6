# Sinter Burden Optimizer — Streamlit Dashboard v6

A redesigned industrial dashboard for the Hospet sinter burden optimization model.

## Included

- Kalyani Steels + Mukand logos in the sidebar
- Task-management inspired workspace layout
- Creative dark industrial theme
- Left navigation with grouped sections
- Right-side optimizer brief / quality watch
- Color-coded KPI cards
- Donut burden composition: Iron Ore → Flux → Recycle → Fuel
- Color-coded result tables with group accents and status badges
- TOTAL rows in burden/cost result tables
- Editable Price and RM Stock
- Material availability toggle
- Raw-material chemistry view
- Optimization results
- Manual burden adjustment
- Proportional redistribution
- Apply & Re-run Optimizer
- What-if analysis
- Bottleneck analysis
- Reports and CSV download
- Excel upload / restore built-in chemistry
- PuLP/CBC optimization engine kept separately in `optimizer.py`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## GitHub + Streamlit Community Cloud

Push the entire folder to GitHub. In Streamlit Community Cloud, select the repository and `app.py` as the main file.

Do not delete the `assets` folder because it contains the two company logos.

## Important

The optimization logic is based on the supplied Sinter Burden Optimizer backend. The UI layer has been redesigned without changing the core optimization engine.
