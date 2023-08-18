import aiosqlite

# Define the path for the SQLite database
db_path = "translations.db"

async def initialize_db():
    """Initialize the database and create tables if they don't exist."""
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.cursor()
        await cursor.execute("""
            CREATE TABLE IF NOT EXISTS translations (
                id INTEGER PRIMARY KEY,
                button_id TEXT NOT NULL UNIQUE,
                translation TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await db.commit()

async def insert_translation(button_id, translation):
    """Insert a new translation into the database."""
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.cursor()
        await cursor.execute("INSERT OR REPLACE INTO translations (button_id, translation) VALUES (?, ?)", (button_id, translation))
        await db.commit()

async def retrieve_translation(button_id):
    """Retrieve a translation from the database based on the button_id."""
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.cursor()
        await cursor.execute("SELECT translation FROM translations WHERE button_id = ?", (button_id,))
        translation = await cursor.fetchone()
        return translation[0] if translation else None

async def delete_old_translations(hours=12):
    """Delete translations that are older than the specified number of hours."""
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.cursor()
        await cursor.execute("DELETE FROM translations WHERE timestamp < datetime('now', '-{} hours')".format(hours))
        await db.commit()

# You can call initialize_db() when your bot starts to ensure the table exists.
