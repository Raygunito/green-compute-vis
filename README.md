# 🌐 Global Data Centers

Interactive dashboard exploring energy (PUE) and water (WUE) efficiency of data centers worldwide — by cooling system, facility type, and geographic location.

**Research question:** Does the choice of cooling system alone determine a data center's energy and water efficiency, and where in the world do these trade-offs manifest?

## Data

[Global Data Center & AI Water/Electricity Usage](https://www.kaggle.com/datasets/ashyou09/global-data-center-and-ai-waterelectricity-usage) - 17,313 facilities, 2019–2025.

## Structure

```
src/
├── app.py          # Streamlit dashboard
├── style.css       # Custom CSS
data/
└── data_center_hybrid.csv
```

## Run

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

## Authors
- [@Raygunito aka Laurent](https://github.com/Raygunito)
- [@alexandreyou aka Alexandre](https://github.com/alexandreyou)