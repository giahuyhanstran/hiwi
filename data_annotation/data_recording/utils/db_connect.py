from pg import DB


class DBConnector:
    def __init__(self, dbname: str = 'data', host: str = 'KI-MV-NUC', port: int = 5432,
                 user: str = 'postgres', passwd: str = 'nosoex'):
        self.__dbname = dbname
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__connection: DB = None

    def connect(self):
        self.__connection = DB(dbname=self.__dbname, host=self.__host, port=self.__port, user=self.__user,
                               passwd=self.__passwd)
        print('Connect to DB with adress ' + self.__host + ':' + str(self.__port) + ' ...')

    def send_query(self, query: str):
        data = self.__connection.query(query)
        print('Send query...')
        return data

    def get_tables(self) -> list:
        tables = self.__connection.get_tables()
        return tables
