# Tubes-PBO-2-OOP
Olympic Medal Prediction and SQL Interaction
This Python script performs web scraping, data analysis, prediction, and SQL database interactions related to Olympic medal tables. It includes functionalities such as scraping medal tables from Wikipedia, predicting podiums, visualizing statistics, and interacting with an SQL database to create, read, update, and delete data.

Dependencies
pandas: Used for data manipulation and analysis.
requests: Used for making HTTP requests to fetch web pages.
BeautifulSoup: A library for pulling data out of HTML and XML files.
tabulate: Helps in creating formatted tables from pandas dataframes.
mysql-connector: Allows Python to connect to MySQL databases.
matplotlib: Used for data visualization through plotting.

Usage
Run the Script:
Execute the script using a Python interpreter (e.g., python script_name.py).
Make sure to have the required dependencies installed (pip install pandas requests beautifulsoup4 tabulate mysql-connector-python matplotlib).

Scraping and Prediction:
The script scrapes medal tables from Wikipedia for three Asian Games editions (2014, 2018, 2022) and predicts the podium for the next competition based on the calculated scores.

SQL Interaction:
The script interacts with a MySQL database for creating tables, inserting, reading, updating, and deleting data.
Modify the SQL class with your MySQL database credentials (host, user, password, database).

View Statistics:
The script provides a menu to view statistics for each scraped/predicted table.
Options include plotting top nations, visualizing medal distributions, and analyzing the distribution of total scores.

Files Generated
table_1_with_scores.csv, table_2_with_scores.csv, table_3_with_scores.csv: CSV files containing scraped medal tables with calculated scores.
prediction.csv: CSV file containing the predicted podium and medal distribution for the next competition.

Note
The script uses a global list of Wikipedia links (table_links) for scraping. Ensure these links are valid and correspond to the desired tables.
Make sure to adjust the SQL connection details according to your MySQL database.

Additional Information
The script serves as a sample and can be extended for other Olympic events or customized for different websites with medal information.
Feel free to adapt and enhance the script based on your specific requirements.

Author: tgrrmdhn

Date: 05/01/2024

License: This project is licensed under the MIT License.
