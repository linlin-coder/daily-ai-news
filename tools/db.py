"""SQLite 数据库模块 — 存储每日报告和文章数据"""

import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
DB_PATH = os.path.join(DB_DIR, 'daily_ai_news.db')


def _get_conn():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """初始化数据库表"""
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE NOT NULL,
            title TEXT,
            digest TEXT,
            cover_path TEXT,
            thumb_media_id TEXT,
            draft_media_id TEXT,
            chart_count INTEGER DEFAULT 0,
            article_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            source TEXT,
            score INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            summary TEXT,
            url TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (report_id) REFERENCES reports(id)
        );

        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            topic TEXT NOT NULL,
            queries TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL,
            file_path TEXT,
            remote_url TEXT,
            caption TEXT,
            inserted_at TEXT,
            FOREIGN KEY (report_id) REFERENCES reports(id)
        );
    """)
    conn.close()


def save_report(date, title, digest, cover_path='', thumb_media_id='',
                draft_media_id='', chart_count=0, article_count=0):
    """保存或更新每日报告记录"""
    conn = _get_conn()
    conn.execute("""
        INSERT INTO reports (date, title, digest, cover_path, thumb_media_id,
                             draft_media_id, chart_count, article_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            title=excluded.title, digest=excluded.digest,
            cover_path=excluded.cover_path, thumb_media_id=excluded.thumb_media_id,
            draft_media_id=excluded.draft_media_id, chart_count=excluded.chart_count,
            article_count=excluded.article_count
    """, (date, title, digest, cover_path, thumb_media_id,
          draft_media_id, chart_count, article_count))
    conn.commit()
    report_id = conn.execute("SELECT id FROM reports WHERE date=?", (date,)).fetchone()[0]
    conn.close()
    return report_id


def save_articles(report_id, articles):
    """批量保存文章"""
    conn = _get_conn()
    # 清除旧数据
    conn.execute("DELETE FROM articles WHERE report_id=?", (report_id,))
    for art in articles:
        conn.execute("""
            INSERT INTO articles (report_id, title, source, score, comments, summary, url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (report_id, art.get('title', ''), art.get('source', ''),
              art.get('score', 0), art.get('comments', 0),
              art.get('summary', ''), art.get('url', '')))
    conn.commit()
    conn.close()


def save_charts(report_id, charts):
    """保存图表记录"""
    conn = _get_conn()
    conn.execute("DELETE FROM charts WHERE report_id=?", (report_id,))
    for img_url, caption, file_path in charts:
        conn.execute("""
            INSERT INTO charts (report_id, file_path, remote_url, caption, inserted_at)
            VALUES (?, ?, ?, ?, datetime('now','localtime'))
        """, (report_id, file_path, img_url, caption))
    conn.commit()
    conn.close()


def save_topic(date, topic, queries=None):
    """保存当天的搜索主题"""
    conn = _get_conn()
    conn.execute("""
        INSERT INTO topics (date, topic, queries) VALUES (?, ?, ?)
    """, (date, topic, json.dumps(queries or [])))
    conn.commit()
    conn.close()


def get_recent_reports(limit=7):
    """获取最近 N 天的报告"""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT r.*, GROUP_CONCAT(a.title, '||') as article_titles
        FROM reports r
        LEFT JOIN articles a ON a.report_id = r.id
        GROUP BY r.id
        ORDER BY r.date DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_report_by_date(date):
    """获取指定日期的报告"""
    conn = _get_conn()
    report = conn.execute("SELECT * FROM reports WHERE date=?", (date,)).fetchone()
    if report:
        report = dict(report)
        articles = conn.execute(
            "SELECT * FROM articles WHERE report_id=?", (report['id'],)
        ).fetchall()
        report['articles'] = [dict(a) for a in articles]
    else:
        report = None
    conn.close()
    return report


def get_stats():
    """获取统计信息"""
    conn = _get_conn()
    total_reports = conn.execute("SELECT count(*) FROM reports").fetchone()[0]
    total_articles = conn.execute("SELECT count(*) FROM articles").fetchone()[0]
    total_charts = conn.execute("SELECT count(*) FROM charts").fetchone()[0]
    conn.close()
    return {
        'total_reports': total_reports,
        'total_articles': total_articles,
        'total_charts': total_charts,
    }


def get_recent_article_titles(days=7):
    """获取最近 N 天已覆盖的文章标题（用于去重）"""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT DISTINCT a.title FROM articles a
        JOIN reports r ON a.report_id = r.id
        WHERE r.date >= date('now', '-' || ? || ' days', 'localtime')
    """, (days,)).fetchall()
    conn.close()
    return [row['title'] for row in rows]


def get_recent_article_keywords(days=7):
    """获取最近 N 天已覆盖文章的关键词（用于模糊去重）"""
    conn = _get_conn()
    rows = conn.execute("""
        SELECT DISTINCT a.title FROM articles a
        JOIN reports r ON a.report_id = r.id
        WHERE r.date >= date('now', '-' || ? || ' days', 'localtime')
    """, (days,)).fetchall()
    conn.close()

    # 提取有意义的中文词组（2-8字），跳过无意义碎片
    keywords = set()
    stopwords = {'的', '了', '是', '在', '和', '与', '被', '将', '对', '为',
                 '个', '到', '从', '这', '那', '都', '也', '还', '就', '用',
                 '能', '会', '要', '让', '来', '又', '最', '但', '却', '更',
                 '是否', '使用', '关于', '进行', '以及', '通过', '可以',
                 'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on',
                 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'has',
                 'how', 'what', 'why', 'when', 'who'}
    for row in rows:
        title = row['title']
        import re
        # 按标点和空格分割
        parts = re.split(r'[，。、；：！？\s\|/·""「」\[\]（）\(\)]+', title)
        for part in parts:
            part = part.strip().lower()
            if len(part) < 2 or part in stopwords:
                continue
            # 短词组直接加入
            if 2 <= len(part) <= 8:
                keywords.add(part)
            # 长标题也要拆出核心词（按"的/了/是/在/和"等常用连接词分割）
            elif len(part) > 8:
                sub_parts = re.split(r'[的是在和与被将对为让来又最但更]', part)
                for sp in sub_parts:
                    sp = sp.strip()
                    if 2 <= len(sp) <= 6 and sp not in stopwords:
                        keywords.add(sp)
    return keywords


def is_duplicate(title, keywords=None):
    """检查文章标题是否与最近已覆盖的内容重复"""
    if keywords is None:
        keywords = get_recent_article_keywords(days=7)

    title_lower = title.lower()

    # 精确匹配
    recent_titles = get_recent_article_titles(days=7)
    for rt in recent_titles:
        if title_lower == rt.lower():
            return True

    # 对新标题也做分割，检查关键词重叠
    import re
    title_parts = re.split(r'[，。、；：！？\s\|/·""「」\[\]（）\(\)]+', title_lower)
    title_words = {p.strip() for p in title_parts if len(p.strip()) >= 2}

    # 检查：新标题的词组是否在已覆盖关键词中
    overlap = title_words & keywords
    if len(overlap) >= 1:
        return True

    # 检查：新标题是否包含已覆盖的关键词子串
    for kw in keywords:
        if len(kw) >= 2 and kw in title_lower:
            return True

    return False


def filter_duplicates(articles):
    """过滤掉重复文章，返回去重后的列表"""
    keywords = get_recent_article_keywords(days=7)
    unique = []
    seen_titles = set()
    for art in articles:
        title = art.get('title', '')
        if title in seen_titles:
            continue
        if is_duplicate(title, keywords):
            continue
        seen_titles.add(title)
        unique.append(art)
    return unique


# 初始化
init_db()
