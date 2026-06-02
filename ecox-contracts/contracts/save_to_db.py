import sqlite3
from datetime import datetime

def save_cid_to_db(filename, cid):
    # Database connect karein
    conn = sqlite3.connect('ecox-contracts/contracts/fingerprints.db')
    cursor = conn.cursor()
    
    # Table create karein agar nahi bani hui
    cursor.execute('''CREATE TABLE IF NOT EXISTS file_records 
                      (filename TEXT, cid TEXT, timestamp TEXT)''')
    
    # Data insert karein
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO file_records VALUES (?, ?, ?)", (filename, cid, timestamp))
    
    conn.commit()
    conn.close()
    print(f"✅ Data saved to fingerprints.db! CID: {cid}")

# Test run
if __name__ == "__main__":
    save_cid_to_db('image_to_test.jpeg', 'QmYcPPbBmZpd6WewsMmcUR49rJUDDTwV4SxNbAZiQkfiwn')