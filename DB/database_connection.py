import psycopg2


class Database:
    def __init__(self):
        self.dbname = 'rlkrficv'
        self.user = 'rlkrficv'
        self.password = 'iMVbx_wb98BoIJCdR26L4Ki3wOBlSwxq'
        self.host = 'rajje.db.elephantsql.com'

        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = psycopg2.connect(dbname=self.dbname, user=self.user, password=self.password, host=self.host)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
