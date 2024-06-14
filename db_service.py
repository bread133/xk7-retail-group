import time
import numpy
import psycopg2.pool
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extras import LoggingConnection, LoggingCursor
from psycopg2.extensions import register_adapter, AsIs
from typing import Tuple
from default_logger import logger

register_adapter(numpy.int64, AsIs)


class MyLoggingCursor(LoggingCursor):
    def execute(self, query, vars=None):
        self.timestamp = time.time()
        return super(MyLoggingCursor, self).execute(query, vars)

    def callproc(self, procname, vars=None):
        self.timestamp = time.time()
        return super(MyLoggingCursor, self).callproc(procname, vars)


class MyLoggingConnection(LoggingConnection):
    def filter(self, msg, curs):
        return msg.decode(psycopg2.extensions.encodings[self.encoding], 'replace') + "   %d ms" % int(
            (time.time() - curs.timestamp) * 1000)

    def cursor(self, *args, **kwargs):
        kwargs.setdefault('cursor_factory', MyLoggingCursor)
        return LoggingConnection.cursor(self, *args, **kwargs)


class ConnectionFromPool:
    """
    Context Manager issues a connection from the pool.
    In case of an error, cancels the transaction.
    """

    def __init__(self, pool: psycopg2.pool.AbstractConnectionPool):
        self.pool = pool
        self.conn = None
        self.exception = None

    def __enter__(self):
        self.conn = self.pool.getconn()
        if self.conn is not None:
            self.conn.initialize(logger)
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):

        if exc_type is not None:
            self.exception = exc_val

            if self.conn:
                self.conn.rollback()

            self.pool.putconn(self.conn)

            return False
        else:
            if self.conn:
                self.conn.commit()

            self.pool.putconn(self.conn)

            return True


class DBService:
    def __init__(self, min_conn: int, max_conn: int, config):
        """
        Creates a service to work with the database. Uses the connection pool.

        :param min_conn: minimum number of connections,
        :param max_conn: the maximum number of connections,
        :param config: connection parameters.
        """
        self.pool = psycopg2.pool.SimpleConnectionPool(min_conn, max_conn,
                                                       connection_factory=MyLoggingConnection, **config)

    def add_content(self, title, duration) -> int:
        """
        Adds a new content with 'title' and 'duration' fields.

        :return: content id from the database.
        """

        query = """ INSERT INTO content(title, duration)
                    VALUES (%s, %s)
                    RETURNING id;
                """

        id = None

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (title, duration,))

                    rows = cur.fetchone()
                    if rows:
                        id = rows[0]

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return id

    def get_content_by_id(self, id: int) -> Tuple[str, int]:
        """
        Getting content data by id content.

        :param: id content.

        :return: content data (title and duration in seconds).
        """

        query = """ SELECT title, duration
                    FROM content
                    WHERE id = %s;
                """

        data = None

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (id,))

                    rows = cur.fetchone()
                    if rows:
                        data = rows[0:2]

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return data

    def delete_content_by_id(self, id: int) -> bool:
        """
        Deletes content with the specified id.

        Note: does not remove data with the specified id from child tables.
            To do so, use the 'cascadeDeleteContentById' method.

        :param: id content.

        :return: Boolean value that tells whether the content was deleted.
        """

        query = """ DELETE FROM content WHERE id = %s; """
        result = False

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (id,))

                    if cur.rowcount > 0:
                        result = True

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return result

    def cascade_delete_content_by_id(self, id: int) -> bool:
        """
        Performs cascading deletion of content.

        Note: will delete data from child tables where id_context = id.

        :param: id content

        :return: Boolean value that tells whether the content was deleted.
        """

        query = """ DELETE FROM snapshot_audio WHERE id_content = %s;
                    DELETE FROM snapshot_video WHERE id_content = %s;
                    DELETE FROM content WHERE id = %s;
                """
        result = False

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (id, id, id,))

                    if cur.rowcount > 0:
                        result = True

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return result

    def add_audio_snapshot(self, id_content, timestamp, hash):
        """
        Adds a new audio snapshot with 'id_content', 'timestamp' and 'hash' fields.

        :param id_content: id content
        :param timestamp: snapshot time
        :param hash: snapshot hash

        :return: Audio snapshot id from the database.
        """

        query = """ INSERT INTO snapshot_audio(id_content, timestamp, hash)
                    VALUES (%s, %s, %s)
                    RETURNING id;
                """

        id = None

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (id_content, timestamp, hash,))

                    rows = cur.fetchone()
                    if rows:
                        id = rows[0]

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return id

    def add_audio_snapshots(self, data: list[Tuple[int, int, str]]):
        """
        Adds a list of audio snapshot data.

        :param data: list with tuple elements - 'id_content', 'timestamp' and 'hash'.

        :return: two values: id of the first inserted line and the number of inserted elements.
        """

        query = """ INSERT INTO snapshot_audio(id_content, timestamp, hash)
                    VALUES %s
                """

        result = []

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    execute_values(cur, query, data)
                    # rows = cur.fetchone()
                    # if rows:
                    #     result = rows[0], cur.rowcount

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return result

    def get_audio_snapshots_by_hash(self, hash) -> list[Tuple[int, int]]:
        """
        Searches all audio snapshots for the given 'hash' value.

        :param hash: snapshot hash.

        :return: list of found rows with 'id_content' and 'timestamp'.
        """

        query = """ SELECT id_content, timestamp
                    FROM snapshot_audio
                    WHERE hash = %s;
                """
        data = []

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (hash,))

                    rows = cur.fetchall()
                    if cur.rowcount > 0:
                        data = rows

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return data

    def get_audio_snapshots_by_hashes(self, hashes: list[str]) -> list[Tuple[int, int, str]]:
        """
        Performs a hash search and returns matches from the database

        :param hashes: - list of snapshot hash

        :return: list of hashes from elements (‘id_content’, ‘timestamp’, ‘hash’)
        """

        query = """ SELECT id_content, timestamp, hash
                    FROM snapshot_audio
                    WHERE hash IN %s
                    
                """

        data = []

        try:
            with ConnectionFromPool(self.pool) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (tuple(hashes),))

                    rows = cur.fetchall()
                    if cur.rowcount > 0:
                        data = rows

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f'Exception: {error}')

        finally:
            return data
