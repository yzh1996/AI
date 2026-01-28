import pymysql
import pandas as pd
from typing import List, Dict, Any


class StarRocksReader:
    """StarRocks数据读取类"""

    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        """
        初始化StarRocks连接

        Args:
            host: StarRocks服务器地址
            port: 端口号，默认9030
            user: 用户名
            password: 密码
            database: 数据库名
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print(f"成功连接到StarRocks: {self.host}:{self.port}/{self.database}")
        except Exception as e:
            print(f"连接失败: {e}")
            raise

    def execute_query(self, sql: str) -> List[Dict[str, Any]]:
        """
        执行SQL查询并返回结果

        Args:
            sql: SQL查询语句

        Returns:
            查询结果列表
        """
        if not self.connection:
            self.connect()

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql)
                results = cursor.fetchall()
                print(f"查询成功，返回 {len(results)} 条记录")
                return results
        except Exception as e:
            print(f"查询失败: {e}")
            raise

    def query_to_dataframe(self, sql: str) -> pd.DataFrame:
        """
        执行查询并返回pandas DataFrame

        Args:
            sql: SQL查询语句

        Returns:
            pandas DataFrame
        """
        results = self.execute_query(sql)
        return pd.DataFrame(results)

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            print("连接已关闭")

    def __enter__(self):
        """支持with语句"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持with语句"""
        self.close()


# 使用示例
if __name__ == "__main__":
    # 配置连接信息
    config = {
        "host": "localhost",  # StarRocks服务器地址
        "port": 9030,  # 查询端口，默认9030
        "user": "root",  # 用户名
        "password": "",  # 密码
        "database": "test_db"  # 数据库名
    }

    # 方式1: 使用with语句（推荐）
    with StarRocksReader(**config) as reader:
        # 执行查询
        sql = "SELECT * FROM your_table LIMIT 10"
        results = reader.execute_query(sql)

        # 打印结果
        for row in results:
            print(row)

        # 或者转换为DataFrame
        df = reader.query_to_dataframe(sql)
        print("\nDataFrame格式:")
        print(df.head())

    # 方式2: 手动管理连接
    # reader = StarRocksReader(**config)
    # reader.connect()
    # results = reader.execute_query("SELECT * FROM your_table LIMIT 10")
    # reader.close()
