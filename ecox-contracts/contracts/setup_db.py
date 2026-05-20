import psycopg2

def create_table():
    try:
        # Apni database details yahan likho
        conn = psycopg2.connect(
            dbname="postgres", user="postgres", password="mskbh2009", host="localhost"
        )
        cur = conn.cursor()
        
        # Table banane ki command
        cur.execute('''
            CREATE TABLE IF NOT EXISTS processed_images (
                id SERIAL PRIMARY KEY,
                hash VARCHAR(256) UNIQUE NOT NULL,
                user_id VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_image_hash ON processed_images(hash);
        ''')
        
        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database Table 'processed_images' kamyabi se ban gayi hai!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    create_table()