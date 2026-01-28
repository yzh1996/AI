import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse
import logging
pd.set_option('display.max_columns', None)  # 显示所有列
pd.set_option('display.max_rows', None)     # 显示所有行
pd.set_option('display.width', None)        # 不换行
pd.set_option('display.max_colwidth', None) # 显示完整的列内容
class StarRocksAdvancedClient:
    def __init__(self, host, port, user, password, database):
        # 对密码进行URL编码（如果包含特殊字符）
        encoded_password = urllib.parse.quote_plus(password)

        # 创建SQLAlchemy连接字符串
        self.connection_string = (
            f"starrocks://{user}:{encoded_password}@{host}:{port}/{database}"
        )

        self.engine = create_engine(self.connection_string, pool_pre_ping=True)

    def query_to_dataframe(self, sql, params=None, chunksize=None):
        """
        使用pandas直接读取SQL结果

        Args:
            sql: SQL查询语句
            params: 查询参数
            chunksize: 分批读取大小（用于大数据量）
        """
        try:
            if chunksize:
                # 分批读取大数据集
                return pd.read_sql(sql, self.engine, chunksize=chunksize)
            else:
                # 直接读取全部数据
                return pd.read_sql(sql, self.engine)

        except Exception as e:
            logging.error(f"Pandas查询失败: {str(e)}")
            raise e

    def execute_with_params(self, sql, params_dict):
        """使用参数化查询（防SQL注入）"""
        with self.engine.connect() as conn:
            result = conn.execute(text(sql), params_dict)
            return result.fetchall()

    def get_table_info(self, table_name):
        """获取表结构信息"""
        sql = f"""
        SELECT 
            COLUMN_NAME,
            DATA_TYPE,
            IS_NULLABLE,
            COLUMN_DEFAULT,
            COLUMN_COMMENT
        FROM information_schema.COLUMNS 
        WHERE TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
        """
        return self.query_to_dataframe(sql)


# 使用示例
def advanced_usage_example():
    # 初始化客户端
    client = StarRocksAdvancedClient(
        host="your-starrocks-host",
        port=9030,
        user="your_username",
        password="your_password",
        database="your_database"
    )

    # 1. 基本查询
    sql = "SELECT * FROM live_base LIMIT 10"
    df = client.query_to_dataframe(sql)
    print(f"获取到 {len(df)} 行数据")

    # # 2. 参数化查询（推荐）
    # param_sql = """
    # SELECT * FROM user_behavior
    # WHERE event_date >= :start_date
    #     AND event_date <= :end_date
    #     AND event_type = :event_type
    # LIMIT 100
    # """
    #
    # params = {
    #     'start_date': '2024-01-01',
    #     'end_date': '2024-01-31',
    #     'event_type': 'purchase'
    # }
    #
    # result_df = client.query_to_dataframe(param_sql, params)
    # print(result_df.head())
    #
    # # 3. 获取表结构
    # table_info = client.get_table_info('sales_table')
    # print("表结构信息:")
    # print(table_info)

# if __name__ == "__main__":
def main(sql:str):
    """
    参数:sql 是要执行的select 语句(必须)
    """
    # 初始化客户端
    client = StarRocksAdvancedClient(
        host="192.168.8.33",
        port=2030,  # 默认查询端口
        user="root",
        password="quxing2021",
        database="donggua"
    )

    # 示例1：基本查询
    # sql = "SELECT * FROM live_base LIMIT 1"
    df = client.query_to_dataframe(sql)
    return df
    # print(df)
    # print(f"获取到 {len(df)} 行数据")

    # df1 = client.advanced_usage_example()
    # print(df1.head())