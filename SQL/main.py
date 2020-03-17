import mysql.connector
import matplotlib
import matplotlib.pyplot

try:
    connection = mysql.connector.connect(host='192.168.0.151',
                                         database='pinet_db',
                                         user='tom',
                                         password='Catapi11ar-')

    if connection.is_connected():
        sql_select_Query = "SELECT timestamp,temperature FROM env_sensors WHERE timestamp BETWEEN '2020-03-17 00:00' AND '2020-03-17 23:59'"
        cursor = connection.cursor()
        cursor.execute(sql_select_Query)
        records = cursor.fetchall()
        print("Total number of rows in env_sensors is: ", cursor.rowcount)

    ts = [ r[0] for r in records ]
    d = [ r[1] for r in records ]

    matplotlib.pyplot.plot(ts,d)
    matplotlib.pyplot.ylim((0,25))
    matplotlib.pyplot.show()


except mysql.connector.Error as e:
    print("Error reading data from MySQL table", e)
finally:
    if (connection.is_connected()):
        connection.close()
        cursor.close()
        print("MySQL connection is closed")
