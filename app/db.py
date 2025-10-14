import sqlite3
from datetime import datetime
from hashlib import sha256

from werkzeug.security import generate_password_hash, check_password_hash

from app import config, utils


def get_conn():
    conn = sqlite3.connect(config.config["app"]["db_path"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> bool:
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("BEGIN TRANSACTION;")
        c.execute("PRAGMA foreign_keys = ON;")
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL,
                verified_time_ts INTEGER NOT NULL,
                group_num INTEGER NOT NULL
            );
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users_not_verified (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT NOT NULL,
                verify_token TEXT UNIQUE NOT NULL
            );
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS invitation_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invitation_code TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                create_time_ts INTEGER NOT NULL,
                expire_time_ts INTEGER NOT NULL
            );
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS profile_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER NOT NULL,
                server_common_name TEXT NOT NULL,
                common_name TEXT NOT NULL,
                request_time_ts INTEGER NOT NULL,
                is_rejected BOOL NOT NULL,
                FOREIGN KEY(uid) REFERENCES users(id)
            );
        """
        )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def user_exists(username: str) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        SELECT EXISTS (
            SELECT 1 FROM users WHERE username = ?
            UNION
            SELECT 1 FROM users_not_verified WHERE username = ?
            UNION
            SELECT 1 FROM invitation_codes WHERE username = ?
        );
    """,
        (
            username,
            username,
            username,
        ),
    )
    result = c.fetchone()[0]
    conn.close()
    return bool(result)


def admin_exists() -> bool:
    return user_exists("Admin")


def add_admin() -> bool:
    if admin_exists():
        return False

    password_hash = generate_password_hash("123456")

    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute(
            """
            INSERT INTO users VALUES (0, 'Admin', ?, '', 0, 0);
        """,
            (password_hash,),
        )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def verify_token_exists(token: str) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users_not_verified WHERE verify_token = ?", (token,))
    result = c.fetchone()
    conn.close()
    return result is not None


def get_not_verified_user_data_with_verify_token(token: str) -> dict:
    if not verify_token_exists(token):
        return {}

    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT username, email FROM users_not_verified WHERE verify_token = ?",
        (token,),
    )
    row = c.fetchone()
    conn.close()
    if row:
        return {"username": row["username"], "email": row["email"]}
    return {}


def add_user_not_verified(username: str, password: str, email: str) -> str | None:
    password_hash = generate_password_hash(password)
    verify_token = sha256(
        f"{username}:{password}:{email}:{datetime.now()}".encode("utf-8")
    ).hexdigest()
    token_len = 24
    while token_len <= 64:
        if not verify_token_exists(verify_token[:token_len]):
            verify_token = verify_token[:token_len]
            break
        token_len += 4
    # although it's almost impossible that two 24-digest tokens collide
    # but just for sure

    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users_not_verified (username, password_hash, email, verify_token) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, verify_token),
        )
        conn.commit()
        return verify_token
    except:
        conn.rollback()
        return None
    finally:
        conn.close()


def verify_user(token: str) -> bool:
    if not verify_token_exists(token):
        return False

    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("BEGIN TRANSACTION;")
        c.execute(
            """
            INSERT INTO users (username, password_hash, email, verified_time_ts, group_num)
                SELECT username, password_hash, email, ?, 1
                FROM users_not_verified WHERE verify_token = ?;
        """,
            (
                int(datetime.now().timestamp()),
                token,
            ),
        )
        c.execute("DELETE FROM users_not_verified WHERE verify_token = ?;", (token,))
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def check_user_password(username: str, password: str) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return check_password_hash(row["password_hash"], password)
    return False


def change_user_password(username: str, new_password: str) -> bool:
    conn = get_conn()
    c = conn.cursor()

    password_hash = generate_password_hash(new_password)
    try:
        c.execute(
            """
            UPDATE users SET password_hash = ?
            WHERE username = ?;
        """,
            (
                password_hash,
                username,
            ),
        )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_uid_with_username(username: str) -> int:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        try:
            return int(row["id"])
        except:
            return -1
    return -1


def get_username_with_invitation_code(code: str) -> str | None:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT username FROM invitation_codes WHERE invitation_code = ?", (code,)
    )
    row = c.fetchone()
    conn.close()
    if row is None:
        return None
    return row["username"]


def invitation_code_exists(code: str) -> bool:
    return get_username_with_invitation_code(code) is not None


def generate_invitation_code(username: str) -> str | None:
    if user_exists(username):
        return None

    code = utils.generate_random_str(12)
    while invitation_code_exists(code):
        code = utils.generate_random_str(12)

    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO invitation_codes (invitation_code, username, create_time_ts, expire_time_ts) VALUES (?, ?, ?, ?);",
            (code, username, int(datetime.now().timestamp()), -1),
        )
        conn.commit()
        return code
    except:
        conn.rollback()
        return None
    finally:
        conn.close()


def list_invitation_code() -> list | None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM invitation_codes;")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def pop_invitation_code(code: str) -> None:
    if not invitation_code_exists(code):
        return

    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("DELETE FROM invitation_codes WHERE invitation_code = ?", (code,))
        conn.commit()
        return
    except:
        conn.rollback()
        return
    finally:
        conn.close()


def add_profile_requests(
    username: str, server_cn: str, common_names: list[str]
) -> bool:
    uid = get_uid_with_username(username)
    if uid == -1:
        return False

    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("BEGIN TRANSACTION;")
        for cn in common_names:
            c.execute(
                """
                INSERT INTO profile_requests (uid, server_common_name, common_name, request_time_ts, is_rejected)
                VALUES (?, ?, ?, ?, FALSE);
            """,
                (
                    uid,
                    server_cn,
                    cn,
                    int(datetime.now().timestamp()),
                ),
            )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def count_user_profile_requests(username: str, server_cn: str = "") -> int:
    uid = get_uid_with_username(username)
    if uid == -1:
        return -1

    conn = get_conn()
    c = conn.cursor()
    if server_cn == "":
        c.execute("SELECT COUNT(*) FROM profile_requests WHERE uid = ?;", (uid,))
    else:
        c.execute(
            "SELECT COUNT(*) FROM profile_requests WHERE uid = ? AND server_common_name = ?;",
            (
                uid,
                server_cn,
            ),
        )
    count = c.fetchone()[0]

    return count


def count_all_profile_requests(server_cn: str = "") -> int:
    conn = get_conn()
    c = conn.cursor()
    if server_cn == "":
        c.execute("SELECT COUNT(*) FROM profile_requests;")
    else:
        c.execute(
            "SELECT COUNT(*) FROM profile_requests WHERE server_common_name = ?;",
            (server_cn,),
        )
    count = c.fetchone()[0]

    return count


def list_user_profile_requests(username: str) -> list | None:
    uid = get_uid_with_username(username)
    if uid == -1:
        return None

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM profile_requests WHERE uid = ?;", (uid,))
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def list_all_profile_requests() -> list | None:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM profile_requests;")
    rows = [dict(row) for row in c.fetchall()]
    conn.close()
    return rows


def profile_request_exists(server_cn: str, common_name: str) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM profile_requests WHERE server_common_name = ? AND common_name = ?;",
        (
            server_cn,
            common_name,
        ),
    )
    result = c.fetchone()
    conn.close()
    return result is not None


def delete_profile_request(server_cn: str, common_name: str) -> bool:
    if not profile_request_exists(server_cn, common_name):
        return False

    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute(
            "DELETE FROM profile_requests WHERE server_common_name = ? AND common_name = ?;",
            (
                server_cn,
                common_name,
            ),
        )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def reject_profile_request(server_cn: str, common_name: str) -> bool:
    if not profile_request_exists(server_cn, common_name):
        return False

    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute(
            """
            UPDATE profile_requests
            SET is_rejected = TRUE
            WHERE server_common_name = ? AND common_name = ?;
        """,
            (
                server_cn,
                common_name,
            ),
        )
        conn.commit()
        return True
    except:
        conn.rollback()
        return False
    finally:
        conn.close()
