import sqlite3

conn = sqlite3.connect("offers.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS offers (
    id TEXT PRIMARY KEY,
    text TEXT,
    url TEXT,
    score INTEGER,
    status TEXT
)
""")

conn.commit()


def add_offer(offer_id, text, url, score):

    cursor.execute("""
        INSERT OR REPLACE INTO offers
        VALUES (?, ?, ?, ?, ?)
    """, (offer_id, text, url, score, "pending"))

    conn.commit()


def get_pending():

    cursor.execute("""
        SELECT * FROM offers
        WHERE status='pending'
        ORDER BY score DESC
    """)

    return cursor.fetchall()


def approve_offer(offer_id):

    cursor.execute("""
        UPDATE offers
        SET status='approved'
        WHERE id=?
    """, (offer_id,))

    conn.commit()


def reject_offer(offer_id):

    cursor.execute("""
        UPDATE offers
        SET status='rejected'
        WHERE id=?
    """, (offer_id,))

    conn.commit()