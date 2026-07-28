# ethiopia-fi-forecastt

Forecasting financial inclusion in Ethiopia using time series methods - 10 Academy KAIM 9 Week 11





\[!\[Python CI](https://github.com/leesol1878/ethiopia-fi-forecast/actions/workflows/unittests.yml/badge.svg)](https://github.com/leesol1878/ethiopia-fi-forecast/actions/workflows/unittests.yml)



\# 🇪🇹 Ethiopia Financial Inclusion Forecasting



> A data-driven forecasting system to track Ethiopia's digital financial transformation and predict financial inclusion outcomes through 2027.



\[!\[Python CI](https://github.com/leesol1878/ethiopia-fi-forecast/actions/workflows/unittests.yml/badge.svg)](https://github.com/leesol1878/ethiopia-fi-forecast/actions/workflows/unittests.yml)

\[!\[Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://python.org)

\[!\[License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

\[!\[Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat\&logo=Streamlit\&logoColor=white)](https://streamlit.io)



\---



\## 📋 Table of Contents



\- \[Business Problem](#business-problem)

\- \[Solution Overview](#solution-overview)

\- \[Key Results](#key-results)

\- \[Quick Start](#quick-start)

\- \[Project Structure](#project-structure)

\- \[Dashboard Demo](#dashboard-demo)

\- \[Technical Details](#technical-details)

\- \[Future Improvements](#future-improvements)

\- \[Author](#author)



\---



\## 🎯 Business Problem



Ethiopia is undergoing a rapid digital financial transformation. Telebirr has grown to \*\*over 54 million users\*\* since launching in 2021, and M-Pesa entered the market in 2023, now serving \*\*over 10 million Ethiopians\*\*. For the first time in 2025, \*\*P2P digital transfers surpassed ATM cash withdrawals\*\*.



Yet despite this progress, the 2024 Global Findex survey reveals that only \*\*49% of Ethiopian adults have a financial account\*\* — just 3 percentage points higher than in 2021.



\*\*Key questions driving this project:\*\*



1\. What drives financial inclusion in Ethiopia?

2\. How do events like product launches, policy changes, and infrastructure investments affect inclusion?

3\. How will financial inclusion evolve through 2027?



\---



\## 💡 Solution Overview



We built a comprehensive forecasting system that:



1\. \*\*Enriches\*\* financial inclusion data with additional observations and impact links

2\. \*\*Analyzes\*\* patterns across 19 indicators and 6 years of data (2014-2025)

3\. \*\*Models\*\* how 10 key events affect 9 financial inclusion indicators

4\. \*\*Forecasts\*\* Account Ownership and Digital Payment Usage for 2025-2027

5\. \*\*Visualizes\*\* everything through an interactive Streamlit dashboard



\### Architecture



┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐

│ Data Layer │────▶│ Analysis │────▶│ Dashboard │

│ - Enrichment │ │ - EDA │ │ - Overview │

│ - Impact Links │ │ - Modeling │ │ - Trends │

│ - Forecasting │ │ - Validation │ │ - Forecasts │

└─────────────────┘ └─────────────────┘ └─────────────────┘







\---



\## 📊 Key Results



| Metric | Value | Confidence |

|--------|-------|------------|

| \*\*Model Validation Error\*\* | <1% | HIGH |

| \*\*Account Ownership (2024)\*\* | 49.0% | HIGH |

| \*\*Mobile Money Penetration (2024)\*\* | 9.45% | HIGH |

| \*\*P2P Transactions (2025)\*\* | 128.3M | HIGH |

| \*\*P2P > ATM (2025)\*\* | ✅ Milestone | HIGH |



\### Forecasts 2025-2027



| Scenario | 2025 | 2026 | 2027 |

|----------|------|------|------|

| \*\*Account Ownership (Base)\*\* | 52.1% | 53.8% | 55.6% |

| \*\*Account Ownership (Optimistic)\*\* | 53.5% | 55.8% | 58.2% |

| \*\*Account Ownership (Pessimistic)\*\* | 51.2% | 52.3% | 53.5% |

| \*\*P2P Transactions (Base)\*\* | 180M | 225M | 280M |

| \*\*P2P Transactions (Optimistic)\*\* | 220M | 285M | 350M |

| \*\*P2P Transactions (Pessimistic)\*\* | 150M | 180M | 220M |



\---



\## 🚀 Quick Start



\### Prerequisites



\- Python 3.9+

\- Git



\### Installation



```bash

\# Clone the repository

git clone https://github.com/leesol1878/ethiopia-fi-forecast.git

cd ethiopia-fi-forecast



\# Create virtual environment

python -m venv venv



\# Activate (Windows)

venv\\Scripts\\activate



\# Activate (Mac/Linux)

source venv/bin/activate



\# Install dependencies

pip install -r requirements.txt



Project Structure
ethiopia-fi-forecast/

├── .github/

│   └── workflows/

│       └── unittests.yml          # CI/CD pipeline

├── data/

│   └── processed/

│       ├── association\_matrix.csv  # Event-indicator matrix

│       ├── ethiopia\_fi\_enriched.csv # Enriched dataset

│       └── forecast\_summary.csv    # Forecast results

├── dashboard/

│   └── app.py                      # Streamlit dashboard

├── notebooks/

│   ├── 01\_data\_exploration.ipynb   # Task 1: Data enrichment

│   ├── 02\_eda\_analysis.ipynb       # Task 2: Exploratory analysis

│   ├── 03\_event\_impact\_modeling.ipynb # Task 3: Impact modeling

│   └── 04\_forecasting.ipynb        # Task 4: Forecasting

├── reports/

│   └── figures/                    # All visualizations

├── src/                            # Modular Python code

│   ├── \_\_init\_\_.py

│   ├── data\_loader.py              # Data loading functions

│   ├── data\_processor.py           # Data processing functions

│   ├── event\_model.py              # Event impact modeling

│   ├── forecast.py                 # Forecasting functions

│   └── utils.py                    # Utility functions

├── tests/                          # Unit tests

│   ├── conftest.py                 # Test fixtures

│   ├── test\_data\_loader.py         # 10 tests

│   ├── test\_data\_processor.py      # 6 tests

│   ├── test\_event\_model.py         # 11 tests

│   └── test\_forecast.py            # 11 tests

├── .flake8                         # Linting config

├── .gitignore

├── pyproject.toml                  # Project metadata

├── pytest.ini                      # Test config

├── requirements.txt

├── README.md

└── FINAL\_REPORT.md                 # Final submission report



🎥 Dashboard Demo

Overview Page

https://reports/figures/dashboard\_overview.png



Forecasts Page

https://reports/figures/forecasts.png



Impact Matrix

https://reports/figures/association\_matrix.png



SHAP Explainability

https://reports/figures/shap\_explainability.png



🔧 Technical Details

Data

Aspect	Details

Total Records	45

Observations	31 (2014-2025)

Events	10

Indicators	19 unique

Data Quality	91.1% HIGH confidence

Sources	Global Findex, GSMA, EthSwitch, Ethio Telecom, Safaricom



Model

Component	Description

Approach	Time series regression with event-impact matrices

Effect Functions	Linear, Step, Sigmoid

Validation	<1% error on historical data

Scenarios	Optimistic, Base, Pessimistic





Evaluation

Metric	Value

Validation Error	<1% (0.25pp difference)

R² (Trend)	0.95+

Confidence Level	95%



🔮 Future Improvements

With more time, we would:



Real-time Data Integration - Connect to EthSwitch API for live P2P data



Regional Analysis - Add regional disaggregation to identify geographic disparities



Machine Learning Models - Implement Random Forest or XGBoost for improved predictions



Gender-Disaggregated Analysis - Collect and analyze more gender-specific data



Agent Network Data - Map agent density and its impact on inclusion



Consumer Survey - Conduct qualitative research on barriers to inclusion



👨‍💻 Author

Tsion Solomon



📧 stsionastw@gmail.com







