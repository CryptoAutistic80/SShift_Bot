import aiosqlite

# Define the path for the SQLite database
db_path = "database/database69.db"

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
            
            await cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_memberships (
                    guild_id TEXT PRIMARY KEY NOT NULL,
                    guild_name TEXT NOT NULL,
                    membership_type TEXT NOT NULL,
                    expiry_date DATETIME NOT NULL,
                    subscription_active BOOLEAN NOT NULL
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

async def add_guild(guild_id, guild_name, membership_type, expiry_date, subscription_active):
    """Insert a new guild membership into the database or return an error if it already exists."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            
            # Check if the guild_id already exists in the database
            await cursor.execute("SELECT 1 FROM guild_memberships WHERE guild_id = ?", (guild_id,))
            existing_guild = await cursor.fetchone()
            
            if existing_guild:
                return "Guild already exists in the database"
            
            # Insert the new guild membership
            await cursor.execute(
                "INSERT INTO guild_memberships (guild_id, guild_name, membership_type, expiry_date, subscription_active) VALUES (?, ?, ?, ?, ?)", 
                (guild_id, guild_name, membership_type, expiry_date, subscription_active))
            await db.commit()
            return "Guild successfully added to the database"
    except aiosqlite.Error as e:
        return f"Database error: {e}"

async def remove_guild(guild_id):
    """Remove a guild membership from the database based on the guild_id and return feedback on the operation."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("DELETE FROM guild_memberships WHERE guild_id = ?", (guild_id,))
            
            # Check if any row was deleted without using await
            changes = db.total_changes
            await db.commit()
            
            if changes > 0:
                return "Guild successfully removed from the database"
            else:
                return "Guild not found in the database"
    except aiosqlite.Error as e:
        return f"Database error: {e}"

async def edit_guild(guild_id, membership_type, expiry_date, subscription_active):
    """Update an existing guild membership's details based on the guild_id."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute(
                "UPDATE guild_memberships SET membership_type = ?, expiry_date = ?, subscription_active = ? WHERE guild_id = ?", 
                (membership_type, expiry_date, subscription_active, guild_id))
            await db.commit()
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def retrieve_guild_membership(guild_id):
    """Retrieve all guild membership details from the database based on the guild_id."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT * FROM guild_memberships WHERE guild_id = ?", (guild_id,))
            membership_details = await cursor.fetchone()
            if membership_details:
                return {
                    "guild_id": membership_details[0],
                    "guild_name": membership_details[1],
                    "membership_type": membership_details[2],
                    "expiry_date": membership_details[3],
                    "subscription_active": membership_details[4]
                }
            return None
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

async def retrieve_active_subscriptions():
    """Retrieve all guild_ids with active subscriptions from the database."""
    try:
        async with aiosqlite.connect(db_path) as db:
            cursor = await db.cursor()
            await cursor.execute("SELECT guild_id FROM guild_memberships WHERE subscription_active = 1")
            active_guilds = await cursor.fetchall()
            return [guild[0] for guild in active_guilds]
    except aiosqlite.Error as e:
        print(f"Database error: {e}")

# You can call initialize_db() when your bot starts to ensure the table exists.