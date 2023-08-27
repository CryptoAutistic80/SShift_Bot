import aiosqlite

# Define the path for the SQLite database
db_path = "database/translations_database.db"

async def initialize_db():
    """Initialize the database and create tables if they don't exist."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS translations (
                    id INTEGER,
                    guild_id TEXT NOT NULL,
                    button_id TEXT NOT NULL UNIQUE,
                    translation TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    original_message_id TEXT NOT NULL,
                    PRIMARY KEY (guild_id, id)
                );
            """)
            await db.commit()
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def insert_translation(guild_id, button_id, translation, original_message_id):
    """Insert a new translation into the database."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(
                "INSERT OR REPLACE INTO translations (guild_id, button_id, translation, original_message_id) VALUES (?, ?, ?, ?)", 
                (guild_id, button_id, translation, original_message_id))
            await db.commit()
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def retrieve_translation(guild_id, button_id):
    """Retrieve a translation from the database based on the guild_id and button_id."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT translation FROM translations WHERE guild_id = ? AND button_id = ?", (guild_id, button_id))
            translation = await cursor.fetchone()
            return translation[0] if translation else None
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def delete_old_translations(guild_id, hours=12):
    """Delete translations that are older than the specified number of hours for a given guild."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("DELETE FROM translations WHERE guild_id = ? AND timestamp < datetime('now', '-{} hours')".format(hours), (guild_id,))
            await db.commit()
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def retrieve_translation_by_original_message_id(guild_id, original_message_id):
    """Retrieve a translation from the database based on the guild_id and original_message_id."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT translation FROM translations WHERE guild_id = ? AND original_message_id = ?", (guild_id, original_message_id))
            translation = await cursor.fetchone()
            return translation[0] if translation else None
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

# You can call initialize_db() when your bot starts to ensure the table exists.
