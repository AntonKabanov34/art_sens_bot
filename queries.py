#Users
QUERIES_USER_INFO = {
    "insert_user_id": "INSERT INTO user_id (user_id) VALUES (?)",
    "insert_or_ignore_user_id": "INSERT OR IGNORE INTO user_id (user_id) VALUES (?)",
    "select_user_id": "SELECT id FROM user_id WHERE user_id = ?",
    "insert_user_info": "INSERT INTO user_info (id, first_name, last_name, username) VALUES (?, ?, ?, ?)",
    "check_user_id_exists": "SELECT EXISTS(SELECT 1 FROM {table_name} WHERE user_id = ?)",
    "select_all_user_id": "SELECT user_id FROM user_id WHERE user_id != ?"
}

#Articles
QUERIES_ARTICLE = {
    "check_article_exists": "SELECT EXISTS(SELECT 1 FROM article WHERE art = ?)",
    "check_file_id_exists": "SELECT EXISTS(SELECT 1 FROM article WHERE art = ? AND file_id IS NOT NULL)",
    "select_file_id": "SELECT file_id FROM article WHERE art = ?",
    "update_file_id": "UPDATE article SET file_id = ? WHERE art = ?"
}

#Admin
QUERIES_ADMIN = {
    "check_admin_exists": "SELECT EXISTS(SELECT 1 FROM admin WHERE user_id = ?)",
    "insert_admin": "INSERT INTO admin (user_id) VALUES (?)",
    "insert_or_ignore_admin": "INSERT OR IGNORE INTO admin (user_id) VALUES (?)",
    "check_admins_table_exists": "SELECT EXISTS(SELECT 1 FROM admin LIMIT 1)"
}

QUERIES_COUNT = {
    "select_counter": "SELECT count FROM {table_name} WHERE name = ?",
    "update_counter": "UPDATE {table_name} SET count = ? WHERE name = ?"
}

QUERIES_DOWNLOADS = {
    "select_user_id": "SELECT id FROM user_id WHERE user_id = ?",
    "select_article_id": "SELECT id FROM article WHERE art= ?",
    "insert_download": "INSERT INTO downloads (user_id, article_id) VALUES (?, ?)"
}


QUERIES_ANALITIC = {
    "count_all_article":"SELECT COUNT(*) AS total_downloads FROM downloads",
    
    "top_articles":"""
    SELECT a.art, COUNT(*) AS download_count
    FROM downloads d
    JOIN article a ON d.article_id = a.id
    GROUP BY a.art
    ORDER BY download_count DESC
    LIMIT 5;
    """,
    
    "top_users":"""
    SELECT u.user_id, COUNT(*) AS download_count
    FROM downloads d
    JOIN user_id u ON d.user_id = u.id
    GROUP BY u.user_id
    ORDER BY download_count DESC
    LIMIT 5;
    """
}