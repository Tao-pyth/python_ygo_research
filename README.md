# Deck Analyzer

Deck Analyzer is a Kivy and KivyMD based application for managing Yu-Gi-Oh! decks and performing card analysis.  The project provides screens for deck creation, card list viewing and editing, and features for importing deck data from CSV files.  Additional scripts are included for downloading card images and running Monte Carlo simulations on deck performance.

## Requirements

- Python 3.8+
- [Kivy](https://kivy.org/)
- [KivyMD](https://kivymd.readthedocs.io/)
- [Pillow](https://pillow.readthedocs.io/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
- [Selenium](https://selenium.dev/) (for image downloading script)
- [matplotlib](https://matplotlib.org/) (for the simulator)

Install dependencies using `pip`:

```bash
pip install kivy kivymd pillow beautifulsoup4 selenium matplotlib
```

## Setup

1. Clone this repository.
2. Ensure the `external_resource` directory exists (ignored by git) for the SQLite database and other exported data.
3. (Optional) Place Japanese fonts under `resource/theme/font` if you need additional fonts.
4. Default configuration is stored in `external_resource/config/config.json`. This file will be created automatically on first run if it does not exist.

## Running the Application

The main menu and deck management screens are launched from `main.py`:

```bash
python3 main.py
```

When started, the app displays a menu allowing you to manage decks, register match data, view statistics or adjust application settings. Deck data is stored locally in an SQLite database under `external_resource/db/ygo_data.db`.

## Additional Tools

- `function/clas/Card_img_download.py` – Selenium based tool to capture card images and save metadata.
- `function/clas/MontecarloSimulator.py` – Monte Carlo simulator for evaluating deck card contribution rates.

These scripts require the dependencies above plus a configured Chrome WebDriver for Selenium.
