# Airbnb User Analytics Dashboard

An interactive multi-page analytics dashboard built with **Dash** and **Plotly**, based on the Airbnb New User Bookings dataset.

## Pages

| Page | Description |
|------|-------------|
| **Overview** | KPI cards, destination distribution, device breakdown, monthly growth |
| **Demographics** | Gender, age, signup method — all filterable by age range, gender and year |
| **Trends** | Monthly signup trends, breakdown by age/gender/device, country-age distribution |

## Interactive Features

- **Dropdowns** — filter by year, gender, breakdown category
- **Range Slider** — filter users by age range
- **Text Input** — search/filter by destination country code
- **Callbacks** — all charts update live based on filter selections

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Place the data files in the same folder as app.py
#    - train_users_2.csv
#    - test_users.csv

# 3. Run the app
python app.py
```

Then open **http://127.0.0.1:8050** in your browser.

## Data

Download the dataset from [Kaggle — Airbnb New User Bookings](https://www.kaggle.com/c/airbnb-recruiting-new-user-bookings/data).

## Author

Taron Khachatryan
