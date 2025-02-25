# Required Libraries
import requests
from lxml import html
from lxml import etree
import os
import psycopg2
from urllib.parse import urljoin
from datetime import datetime

# PostgreSQL Database Credentials (Update these)
DB_NAME = "state_union_addresses"
DB_USER = "postgres"
DB_PASSWORD = "Sushma_02"
DB_HOST = "localhost"  # Change if using a remote server
DB_PORT = "5432"  # Default PostgreSQL port

# Web scraping URLs
MAIN_URL = "https://www.infoplease.com"
SPEECHES_URL = "https://www.infoplease.com/primary-sources/government/presidential-speeches/state-union-addresses"


def connect_to_postgres():
    """Connects to PostgreSQL and creates the database and table if not exists."""
    conn = psycopg2.connect(
        dbname="postgres",  # Connect to default database first
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()

    # Create database if it doesn't exist
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    if not cursor.fetchone():
        cursor.execute(f"CREATE DATABASE {DB_NAME}")

    cursor.close()
    conn.close()

    # Connect to the new database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Create the table if it does not exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS address_table (
            id SERIAL PRIMARY KEY,
            name_of_president VARCHAR(100),
            date_of_union_address DATE,
            link_to_address TEXT,
            filename_address TEXT,
            text_of_address TEXT
        );
    """)
    conn.commit()
    
    return conn, cursor


def insert_row_into_table(cursor, name, date, link, file, text):
    """Inserts a single union address into the PostgreSQL database."""
    cursor.execute("""
        INSERT INTO address_table (name_of_president, date_of_union_address, link_to_address, filename_address, text_of_address)
        VALUES (%s, %s, %s, %s, %s);
    """, (name, date, link, file, text))


def write_to_file(output_directory, file_name, text):
    """Writes the speech to a local file and returns the file path."""
    clean_file_name = file_name.replace(',', '').replace(' ', '_')
    full_file_path = os.path.join(output_directory, f"{clean_file_name}.txt")
    with open(full_file_path, "w", encoding='utf-8') as text_file:
        text_file.write(text)
    return full_file_path


def display_broken_links(broken_links):
    """Displays any broken links encountered while scraping."""
    if broken_links:
        print("\nBroken Links Encountered:")
        for president, date, link in broken_links:
            print(f"- {president} ({date}): {link}")
    else:
        print("\nNo broken links encountered.")


def main():
    """A web scraper that extracts State of the Union address speeches and stores them in a PostgreSQL database."""
    # Connect to PostgreSQL
    conn, cursor = connect_to_postgres()

    # Get main page content
    page = requests.get(SPEECHES_URL)
    tree = html.fromstring(page.content)
    html_etree = etree.ElementTree(tree)

    # Create output directory for speech text files
    output_directory = os.path.join(os.getcwd(), "SpeechFiles")
    os.makedirs(output_directory, exist_ok=True)

    # Create the combined speeches file
    combined_speeches_file = "CombinedStateOfUnionAddresses.txt"
    broken_links = []

    with open(combined_speeches_file, 'w', encoding='utf-8') as combined_file:
        # Navigate using XPath to find speech links
        speech_links = html_etree.xpath('//*//div/dl/dt/span/a')

        # Iterate over each speech element and extract information
        for speech in speech_links:
            full_speech_text = speech.text.strip()
            relative_link = speech.get("href")  # Get the relative URL
            full_link = urljoin(MAIN_URL, relative_link)  # Create full URL

            if '(' in full_speech_text and ')' in full_speech_text:
                president, date = full_speech_text.rsplit("(", 1)
                president = president.strip()
                date = date.strip(")")

                # Handle different date formats and convert to standard format
                try:
                    date = date.replace("th", "").replace("st", "").replace("nd", "").replace("rd", "").strip()
                    date = datetime.strptime(date, "%B %d, %Y").date()  # Convert to date format
                except ValueError:
                    continue  # Skip if date format is incorrect
            else:
                continue

            print(f"Processing speech for {president} ({date})")

            # Extract the speech content
            speech_response = requests.get(full_link)
            speech_tree = html.fromstring(speech_response.content)

            # Find all <p> tags containing speech text
            p_tags = speech_tree.xpath("//*/article/div/div/p")
            speech_text = "\n".join([p.text_content().strip() for p in p_tags])

            # Check if speech text is empty
            if not speech_text.strip():
                print(f"No speech found for {president} ({date})")
                broken_links.append((president, date, full_link))

                # Insert NULL values for missing speeches
                insert_row_into_table(cursor, president, date, full_link, "NULL", "NULL")
                continue

            # Save speech text to a local file
            filename = write_to_file(output_directory, f"{president} ({date})", speech_text)

            # Insert data into PostgreSQL
            insert_row_into_table(cursor, president, date, full_link, filename, speech_text)

            # Append speech to the combined file
            combined_file.write(f"{president} ({date})\n\n{speech_text}\n\n{'-' * 80}\n\n")

    conn.commit()  # Commit changes to the database
    cursor.close()
    conn.close()
    print("\nRecords stored in PostgreSQL database.")
    
    display_broken_links(broken_links)


# Run the script
if __name__ == "__main__":
    main()
