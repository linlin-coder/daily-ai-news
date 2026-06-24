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


# 初始化
init_db()
