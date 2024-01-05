import pandas as pd
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import mysql.connector
import matplotlib.pyplot as plt

class Scrape():
    def __init__(self, url):
        self.url = url

    def scrape_table_wikipedia(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'wikitable sortable plainrowheaders jquery-tablesorter'})
        if table:
            tbody = table.tbody
            rows = tbody.find_all('tr')
            columns = [th.text.replace('\n', '') for th in rows[0].find_all(['th', 'td'])]
            data = []
            for i in range(1, min(7, len(rows))):
                tds = rows[i].find_all(['th', 'td'])
                values = [td.text.replace('\n', '').replace('\xa0', '') for td in tds]
                data.append(values)
            df = pd.DataFrame(data, columns=columns)
            return df

class Prediction(Scrape):
    def __init__(self, url, df):
        super().__init__(url)
        self.df = df

    def calculate_scores(self):
        self.df['Total Scores'] = (
            5 * pd.to_numeric(self.df['Gold'], errors='coerce').fillna(0) +
            2 * pd.to_numeric(self.df['Silver'], errors='coerce').fillna(0) +
            1 * pd.to_numeric(self.df['Bronze'], errors='coerce').fillna(0)
        )
        return self.df.sort_values(by='Total Scores', ascending=False)
    
    def predict_next_competition_podium(self, df_pred):
        total = len(table_links)
        predicted_podium = df_pred.groupby('Nation')['Total Scores'].sum().div(total).nlargest(5).astype(int)
        return predicted_podium
    
    def predict_medals_distribution(self):
        predicted_medals = self.df[['Nation', 'Total Scores']].copy()

        predicted_medals['Gold'] = (self.df['Total Scores'] // 5).astype(int)
        predicted_medals['Silver'] = ((self.df['Total Scores'] % 5) // 2).astype(int)
        predicted_medals['Bronze'] = (self.df['Total Scores'] % 2).astype(int)

        return predicted_medals
    
class Statistics():
    def __init__(self, df):
        self.df = df

    def plot_top_nations(self, n=5):
        top_nations = self.df.nlargest(n, 'Total Scores')

        plt.figure(figsize=(10, 6))
        plt.bar(top_nations['Nation'], top_nations['Total Scores'], color='skyblue')
        plt.xlabel('Nation')
        plt.ylabel('Total Scores')
        plt.title(f'Top {n} Nations in Total Scores')
        plt.show()

    def plot_medals_distribution(self):
        medals_data = self.df[['Gold', 'Silver', 'Bronze']]
        medals_data.plot(kind='bar', stacked=True, figsize=(12, 6))
        plt.xlabel('Nation')
        plt.ylabel('Number of Medals')
        plt.title('Medals Distribution by Nation')
        plt.show()

    def plot_total_scores_distribution(self):
        plt.figure(figsize=(12, 6))
        plt.hist(self.df['Total Scores'], bins=20, color='skyblue', edgecolor='black')
        plt.xlabel('Total Scores')
        plt.ylabel('Frequency')
        plt.title('Distribution of Total Scores')
        plt.show()

class SQL():
    def __init__(self, host, user, password, database):
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor()

    def create(self, mode):
        if mode in range(1, 4):
            table_name = f"Competition{mode}"
            self.sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                Rank INT PRIMARY KEY,
                Nation VARCHAR(255),
                Gold INT,
                Silver INT,
                Bronze INT,
                Total INT,
                Total_Scores INT
            )"""
            try:
                self.cursor.execute(self.sql)
                self.db.commit()
            except Exception as e:
                print(f"Error creating table {table_name}: {e}")
        elif mode == 4:
            table_name = f"Competition{mode}"
            self.sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
                Rank INT AUTO_INCREMENT PRIMARY KEY,
                Nation VARCHAR(255),
                Gold INT,
                Silver INT,
                Bronze INT,
                Total_Scores INT
            )"""
            try:
                self.cursor.execute(self.sql)
                self.db.commit()
            except Exception as e:
                print(f"Error creating table {table_name}: {e}")

    def insert_data(self, mode, table):
        if mode in range(1, 4):
            table_name = f"Competition{mode}"
            self.sql = f"INSERT INTO {table_name} (Rank, Nation, Gold, Silver, Bronze, Total, Total_Scores) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            self.values = []
            for i in range(len(table)):
                row = table.iloc[i]
                values = (
                    int(row['Rank']),
                    row['Nation'],
                    int(row['Gold']),
                    int(row['Silver']),
                    int(row['Bronze']),
                    int(row['Total']),
                    int(row['Total Scores'])
                )
                self.values.append(values)
            try:
                self.cursor.executemany(self.sql, self.values)
                self.db.commit()
            except Exception as e:
                print(f"Error inserting data into table {table_name}: {e}")
        elif mode == 4:
            table_name = f"Competition{mode}"
            self.sql = f"INSERT INTO {table_name} (Nation, Gold, Silver, Bronze, Total_Scores) VALUES (%s, %s, %s, %s, %s)"
            self.values = []
            for i in range(len(table)):
                row = table.iloc[i]
                values = (
                    row['Nation'],
                    int(row['Gold']),
                    int(row['Silver']),
                    int(row['Bronze']),
                    int(row['Total Scores'])
                )
                self.values.append(values)
            try:
                self.cursor.executemany(self.sql, self.values)
                self.db.commit()
            except Exception as e:
                print(f"Error inserting data into table {table_name}: {e}")

    def read(self, mode):
        if mode in range(1, 4):
            table_name = f"Competition{mode}"
            self.sql = f"SELECT * FROM {table_name}"
            try:
                self.cursor.execute(self.sql)
                result = self.cursor.fetchall()
                return result
            except Exception as e:
                print(f"Error reading data from table {table_name}: {e}")
        elif mode == 4:
            table_name = f"Competition{mode}"
            self.sql = f"SELECT * FROM {table_name}"
            try:
                self.cursor.execute(self.sql)
                result = self.cursor.fetchall()
                return result
            except Exception as e:
                print(f"Error reading data from table {table_name}: {e}")

    def update(self, mode, data):
        if mode in range(1, 4):
            table_name = f"Competition{mode}"
            self.sql = f"UPDATE {table_name} SET Total_Scores = %s WHERE Nation = %s"
            try:
                for values in data:
                    self.cursor.execute(self.sql, values)
                    self.db.commit()
                print("Data updated successfully.")
            except Exception as e:
                print(f"Error updating data in table {table_name}: {e}")
        elif mode == 4:
            table_name = f"Competition{mode}"
            self.sql = f"UPDATE {table_name} SET Total_Scores = %s WHERE Nation = %s"
            try:
                for values in data:
                    self.cursor.execute(self.sql, values)
                    self.db.commit()
                print("Data updated successfully.")
            except Exception as e:
                print(f"Error updating data in table {table_name}: {e}")

    def delete(self, mode, nation):
        if mode in range(1, 4):
            table_name = f"Competition{mode}"
            self.sql = f"DELETE FROM {table_name} WHERE Nation = %s"
            try:
                self.cursor.execute(self.sql, (nation,))
                self.db.commit()
            except Exception as e:
                print(f"Error deleting data from table {table_name}: {e}")
        elif mode == 4:
            table_name = f"Competition{mode}"
            self.sql = f"DELETE FROM {table_name} WHERE Nation = %s"
            try:
                self.cursor.execute(self.sql, (nation,))
                self.db.commit()
            except Exception as e:
                print(f"Error deleting data from table {table_name}: {e}")

table_links = [
    "https://en.wikipedia.org/wiki/Archery_at_the_2014_Asian_Games",
    "https://en.wikipedia.org/wiki/Archery_at_the_2018_Asian_Games",
    "https://en.wikipedia.org/wiki/Archery_at_the_2022_Asian_Games"
]

def main():
    global table_1, table_2, table_3
    tables = []
    for i, link in enumerate(table_links, 1):
        data = Scrape(link)
        table_data = data.scrape_table_wikipedia()
        if table_data is not None:
            score = Prediction(link, table_data)
            table_data_with_scores = score.calculate_scores()
            csv_filename = f"table_{i}_with_scores.csv"
            table_data_with_scores.to_csv(csv_filename, index=False)
            print(f"\nDataFrame with scores saved to {csv_filename}\n")
            print(f"\nTable with scores from {link}:\n")
            print(tabulate(table_data_with_scores, headers='keys', tablefmt='fancy_grid'))
            tables.append(table_data_with_scores)

    table_1 = pd.read_csv("table_1_with_scores.csv")
    table_2 = pd.read_csv("table_2_with_scores.csv")
    table_3 = pd.read_csv("table_3_with_scores.csv")

    all_tables = pd.concat(tables).reset_index(drop=True)
    all_tables['Nation'] = all_tables['Nation'].apply(lambda x: x.split('_')[0])

    predicted_podium = score.predict_next_competition_podium(all_tables)
    df_pred = pd.DataFrame(predicted_podium).reset_index()
    df_pred.columns = ['Nation', 'Total Scores']
    df_pred.to_csv("prediction.csv", index=False)
    table_4 = pd.read_csv("prediction.csv")

    prediction_for_table_4 = Prediction(table_links[2], table_4)

    predicted_medals_distribution = prediction_for_table_4.predict_medals_distribution()
    predicted_medals_distribution.to_csv("prediction.csv", index=False)
    print("\nPredicted Medal Distribution for Table 4:")
    print(tabulate(predicted_medals_distribution, headers='keys', tablefmt='fancy_grid'))
    table_4 = pd.read_csv("prediction.csv")

    sql = SQL("localhost", "root", "", "competition")

    while True:
        print("\nMenu:")
        print("1. View Statistics")
        print("2. Access SQL")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            print("\nSelect Table:")
            print("a. Table 1 (Asian Games 2014)")
            print("b. Table 2 (Asian Games 2018)")
            print("c. Table 3 (Asian Games 2022)")
            print("d. Table 4 (Prediction)")

            table_choice = input("Enter your choice (a/b/c/d): ")

            if table_choice == "a":
                stats = Statistics(table_1)
            elif table_choice == "b":
                stats = Statistics(table_2)
            elif table_choice == "c":
                stats = Statistics(table_3)
            elif table_choice == "d":
                stats = Statistics(table_4)
                
            print("\nStatistics Menu:")
            print("a. Plot Top Nations")
            print("b. Plot Medals Distribution")
            print("c. Plot Total Scores Distribution")
            
            stat_choice = input("Enter your choice (a/b/c): ")

            if stat_choice == 'a':
                n = int(input("Enter the number of top nations to plot: "))
                stats.plot_top_nations(n)
            elif stat_choice == 'b':
                stats.plot_medals_distribution()
            elif stat_choice == 'c':
                stats.plot_total_scores_distribution()
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == '2':
            print("\nSQL Menu:")
            print("1. Create Tables")
            print("2. Insert Data")
            print("3. Read Data")
            print("4. Update Data")
            print("5. Delete Data")
            print("6. Back to Main Menu")

            sql_choice = input("Enter your choice (1/2/3/4/5/6): ")

            if sql_choice == '1':
                for i in range(1, 4):
                    sql.create(i)
                sql.create(4)
                print("Tables created successfully.")
            elif sql_choice == '2':
                for i in range(1, 4):
                    sql.insert_data(i, globals()[f'table_{i}'])
                sql.insert_data(4, table_4)
                print("Data inserted successfully.")
            elif sql_choice == '3':
                mode = int(input("Enter the competition mode (1/2/3/4): "))
                result = sql.read(mode)
                print(tabulate(result, headers='keys', tablefmt='fancy_grid'))
            elif sql_choice == '4':
                mode = int(input("Enter the competition mode (1/2/3/4): "))
                update_data = []
                while True:
                    nation = input("Enter the nation to update (or 'exit' to stop): ")
                    if nation.lower() == 'exit':
                        break
                    total_scores = int(input("Enter the new total scores: "))
                    update_data.append((total_scores, nation))
                sql.update(mode, update_data)
                print("Data updated successfully.")
            elif sql_choice == '5':
                mode = int(input("Enter the competition mode (1/2/3/4): "))
                nation_to_delete = input("Enter the nation to delete: ")
                sql.delete(mode, nation_to_delete)
                print("Data deleted successfully.")
            elif sql_choice == '6':
                continue
            else:
                print("Invalid choice. Please enter a valid option.")

        elif choice == '3':
            print("Exiting the program.")
            break

        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()