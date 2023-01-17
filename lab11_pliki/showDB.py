import time
import sqlite3



def main():
    connention = sqlite3.connect("messages.db")
    cursor = connention.cursor()
    cursor.execute("SELECT * FROM messages_log")
    log_entries = cursor.fetchall()
    for a in log_entries:
        print(a[0])
    connention.commit()
    connention.close()

if __name__ == "__main__":
    main()