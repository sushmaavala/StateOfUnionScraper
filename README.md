# State of the Union Scraper

# 🏛️ State of the Union Scraper

This project is a **web scraper** that extracts State of the Union addresses from [InfoPlease](https://www.infoplease.com/) and stores them in a **PostgreSQL database**.

## 📌 Features

- ✅ Scrapes **State of the Union addresses** using Python.
- ✅ Saves speeches to **local text files**.
- ✅ Stores extracted data in a **PostgreSQL database**.
- ✅ Handles **broken links** and skips them.

## 🛠️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/sushmaavala/StateOfUnionScraper.git
cd StateOfUnionScraper

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Configure PostgreSQL Database
1.Make sure PostgreSQL is installed.
2.Update database credentials in main.py.

4️⃣ Run the Scraper
python3 main.py
📂 Output Files
CombinedStateOfUnionAddresses.txt → All speeches combined into one file.
SpeechFiles/ → Individual speech text files.
PostgreSQL Database → Stores extracted data.
📜 License
This project is open-source. Feel free to contribute!








```
