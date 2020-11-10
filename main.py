import sqlite3
import random
import datetime


def createConnection(database):
    connection = None
    try:
        connection = sqlite3.connect(database)
    except sqlite3.Error as e:
        print(e)

    return connection


def createTables(connection):
    cursor = connection.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
        userid integer primary key,
        age integer NOT NULL
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Items (
        itemid integer primary key,
        price real NOT NULL
        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Purchases (
        purchaseid integer primary key,
        userid integer NOT NULL,
        itemid integer NOT NULL,
        date date NOT NULL,
        FOREIGN KEY(userid) REFERENCES Users(userid),
        FOREIGN KEY(itemid) REFERENCES Items(itemid)
        )''')


# Функция, решающая задачу А
def task_1(connection):
    cursor = connection.cursor()
    startDate = datetime.date(2000, 1, 1)  # Дата начала учёта покупок

    print("Задание А:")
    cursor.execute("SELECT sum(price) / (12 * (strftime('%Y', datetime('now')) - strftime('%Y', ?)) + strftime('%m', datetime('now')) - (strftime('%m', ?) - 1)) AS averagePerMonth "
                   "FROM Purchases INNER JOIN Users USING (userid) INNER JOIN Items USING (itemid) WHERE age BETWEEN 18 and 25", (startDate, startDate))
    result = cursor.fetchone()
    print('1)', result[0])

    cursor.execute("SELECT sum(price) / (12 * (strftime('%Y', datetime('now')) - strftime('%Y', ?)) + strftime('%m', datetime('now')) - (strftime('%m', ?) - 1)) AS averagePerMonth "
                   "FROM Purchases INNER JOIN Users USING (userid) INNER JOIN Items USING (itemid) WHERE age BETWEEN 26 and 35", (startDate, startDate))
    result = cursor.fetchone()
    print('2)', result[0])
    print('\n')


# Функция, решающая задачу Б
def task_2(connection):
    cursor = connection.cursor()

    print("Задание Б:")
    cursor.execute("SELECT strftime('%m', date) AS month from Purchases INNER JOIN Users USING (userid) INNER JOIN Items USING (itemid) "
                   "WHERE age >= 35 GROUP BY (strftime('%m', date)) ORDER BY sum(price) DESC LIMIT 1")
    result = cursor.fetchone()
    print(result[0])
    print('\n')


# Функция, решающая задачу В
def task_3(connection):
    cursor = connection.cursor()
    lastYear = datetime.date.today() - datetime.timedelta(days=365)  # Дата год назад

    print("Задание В:")
    cursor.execute("SELECT itemid FROM Purchases INNER JOIN Items USING (itemid) WHERE date >= ? "
                   "GROUP BY itemid ORDER BY sum(price) DESC LIMIT 1", (lastYear,))
    result = cursor.fetchone()
    print(result[0])
    print('\n')


# Функция, решающая задачу Г
def task_4(connection, year):
    cursor = connection.cursor()

    print("Задание Г:")
    cursor.execute("SELECT itemid, sum(price) / (SELECT sum(price) from Purchases INNER JOIN Items USING (itemid) WHERE strftime('%Y', date) = ?) AS share_in_total"
                   " FROM Purchases INNER JOIN Items USING (itemid) WHERE strftime('%Y', date) = ? GROUP BY itemid ORDER BY sum(price) DESC LIMIT 3", (year, year))
    result = cursor.fetchall()
    for row in result:
        print(row[0], row[1], sep='   ')


# Функция генерации данных и добавления их в БД
def generateData(connection):
    cursor = connection.cursor()

    # Генерируются:
    # 500 пользователей возрастом от 18 до 70 лет;
    # 100 товаров с ценой от 100 до 1000;
    # 10000 покупок с датами от 01.01.2000 до сегодняшней;
    a = [(random.randint(18, 70),) for _ in range(500)]
    p = [(round(random.uniform(100, 1000), 2),) for _ in range(100)]
    startDate = datetime.date(2000, 1, 1).toordinal()
    endDate = datetime.date.today().toordinal()
    data = [
        (random.randint(1, 100), random.randint(1, 20), datetime.date.fromordinal(random.randint(startDate, endDate)))
        for _ in range(10000)]

    # Добавление в БД сгенерированных данных
    cursor.executemany("INSERT INTO Users (age) VALUES (?)", a)
    cursor.executemany("INSERT INTO Items (price) VALUES (?)", p)
    cursor.executemany("INSERT INTO Purchases (userid, itemid, date) VALUES (?, ?, ?)", data)

    connection.commit()


def main():
    connection = createConnection('my.db')

    with connection:
        createTables(connection)
        generateData(connection)  # При повторных выполнениях программы данную строку необходимо закомментировать

        task_1(connection)
        task_2(connection)
        task_3(connection)
        task_4(connection, '2015')  # Вторым параметром здесь передаётся год в виде строки


if __name__ == '__main__':
    main()
