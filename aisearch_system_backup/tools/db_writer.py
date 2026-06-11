#!/usr/bin/env python3
"""
db_writer.py — PostgreSQL write interface for all agents
Handles connection pooling, transaction management, and schema enforcement.
"""

import os
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class DBWriter:
    """
    Unified PostgreSQL write interface.
    All writes are transactionally wrapped per pipeline stage.
    """

    def __init__(self, connection_string: Optional[str] = None):
        self.conn_string = connection_string or os.environ.get("DATABASE_URL")
        self._db_conn = None

    def _connect(self):
        """Lazy connection — connect on first write."""
        if self._db_conn is None or self._db_conn.closed:
            import psycopg2
            self._db_conn = psycopg2.connect(self.conn_string)
        return self._db_conn

    def write_run_summary(self, run_data: dict):
        """Write a pipeline run manifest to oracle_runs table."""
        import psycopg2
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO oracle_runs (run_id, brand, started_at, completed_at,
                                     total_queries, failed_queries, status, gaps)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (run_id) DO UPDATE SET
                status = EXCLUDED.status,
                completed_at = EXCLUDED.completed_at,
                failed_queries = EXCLUDED.failed_queries
        """, (
            run_data["run_id"], run_data["brand"], run_data["started_at"],
            run_data.get("completed_at"), run_data["total_queries"],
            run_data["failed_queries"], run_data["status"],
            json.dumps(run_data.get("gaps", [])),
        ))
        conn.commit()
        conn.close()

    def write_extractions(self, extractions: list):
        """Write SIEVE extraction records to brand_mentions table."""
        import psycopg2
        if not extractions:
            return
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        for ext in extractions:
            cur.execute("""
                INSERT INTO brand_mentions (run_id, query_id, brand, engine,
                                           mention_count, sentiment, mention_type, position)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                ext.get("run_id"), ext.get("query_id"), ext.get("brand"),
                ext.get("engine"), ext.get("mention_count", 1),
                ext.get("sentiment"), ext.get("mention_type"), ext.get("position"),
            ))
        conn.commit()
        conn.close()

    def write_competitive_report(self, report: dict):
        """Write RIVAL competitive report as JSONB in oracle_runs.gaps."""
        import psycopg2
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO oracle_runs (run_id, brand, started_at, status, gaps)
            VALUES (%s, %s, NOW(), 'COMPETITIVE_REPORT', %s)
            ON CONFLICT (run_id) DO UPDATE SET gaps = EXCLUDED.gaps
        """, (
            report.get("run_id"), report.get("brand"), json.dumps(report),
        ))
        conn.commit()
        conn.close()

    def write_action_plan(self, plan: dict):
        """Write ORACLE-X recommendations to oracle_recommendations table."""
        import psycopg2
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        for rec in plan.get("recommendations", []):
            cur.execute("""
                INSERT INTO oracle_recommendations
                (rec_id, run_id, rec_type, title, target_query, priority_score,
                 estimated_effort, expected_ai_lift, owner)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (rec_id) DO UPDATE SET
                    status = 'BACKLOG',
                    updated_at = NOW()
            """, (
                rec["id"], plan.get("run_id"), rec["type"], rec["title"],
                rec.get("target_query"), rec.get("priority_score", 0),
                rec.get("estimated_effort"), rec.get("expected_ai_lift"),
                rec.get("owner"),
            ))
        conn.commit()
        conn.close()

    def upsert_citation_node(self, node: dict):
        """Insert citation record into citation_history table."""
        import psycopg2
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO citation_history (run_id, domain, engine, query_id,
                                         mention_count, attributed_page)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            node["run_id"], node["domain"], node["engine"],
            node["query_id"], node.get("mention_count", 1),
            node.get("attributed_page"),
        ))
        conn.commit()
        conn.close()
