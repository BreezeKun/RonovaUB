from .neondb import db

class SudoMethods:

    def __init__(self):
        self.cache: set[int] = set()

    def crt_sudo_tab(self):
        db.execute("""
        CREATE TABLE IF NOT EXISTS sudo_users (
            user_id BIGINT PRIMARY KEY
        );
        """)

    def build_cache(self):
        rows = db.execute("""
        SELECT user_id FROM sudo_users;
        """, fetch=True)

        self.cache = {row[0] for row in rows}
        print(f"[CACHE] Loaded {len(self.cache)} sudo users")

    def add_sudo(self, user_id: int):
        db.execute("""
        INSERT INTO sudo_users (user_id)
        VALUES (%s)
        ON CONFLICT (user_id) DO NOTHING;
        """, (user_id,))

        self.cache.add(user_id)

    def rem_sudo(self, user_id: int):
        db.execute("""
        DELETE FROM sudo_users
        WHERE user_id = %s;
        """, (user_id,))

        self.cache.discard(user_id)

    def get_sudo(self):
        return list(self.cache)

    def is_sudo(self, user_id: int) -> bool:
        return user_id in self.cache


sudo_methods = SudoMethods()
sudo_methods.crt_sudo_tab()