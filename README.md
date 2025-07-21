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
2. Ensure the `external_resource` directory exists (ignored by git). It will be created automatically on first run and stores the SQLite database, logs and other exported data.
3. Default configuration is stored in `resource/json/config.json`. On first launch this file is copied to `external_resource/config/config.json` if it does not already exist. You can edit the copied file to change the KivyMD color palette and theme style used by the application.
   The application uses the Windows standard Japanese font `C:\Windows\Fonts\msgothic.ttc` by default. Enable the custom font option in the settings screen if you wish to upload another font file.

## Running the Application

The main menu and deck management screens are launched from `main.py`:

```bash
python3 main.py
```

When started, the app displays a menu allowing you to manage decks, register match data, view statistics or adjust application settings. Deck data is stored locally in an SQLite database under `external_resource/db/ygo_data.db`.
The current color palette and light/dark style are loaded from `config.json` and can also be changed from the in-app settings screen.

## Additional Tools

  - `function/core/card_img_download.py` – Selenium based tool to capture card images and save metadata.
  - `function/core/monte_carlo_simulator.py` – Monte Carlo simulator for evaluating deck card contribution rates.

These scripts require the dependencies above plus a configured Chrome WebDriver for Selenium.
