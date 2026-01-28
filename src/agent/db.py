import connect
import pandas as pd
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StarRocksClient:
    def __init__(self, host, port, user, password, database=None):
        self.connection_config = {
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'database': database
        }

    def execute_query(self, sql, params=None, return_df=True):
        """
        执行StarRocks查询

        Args:
            sql: SQL查询语句
            params: 查询参数（防止SQL注入）
            return_df: 是否返回DataFrame
        """
        conn = None
        try:
            # 建立连接
            conn = connect(**self.connection_config)
            cursor = conn.cursor()

            # 执行查询
            logger.info(f"执行SQL: {sql}")
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # 获取结果
            if return_df:
                # 获取列名
                columns = [desc[0] for desc in cursor.description]
                # 获取数据并转换为DataFrame
                data = cursor.fetchall()
                df = pd.DataFrame(data, columns=columns)
                logger.info(f"查询成功，返回 {len(df)} 行数据")
                return df
            else:
                result = cursor.fetchall()
                logger.info(f"查询成功，返回 {len(result)} 行数据")
                return result

        except Exception as e:
            logger.error(f"查询执行失败: {str(e)}")
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()


# 使用示例
if __name__ == "__main__":
    # 初始化客户端
    client = StarRocksClient(
        host="192.168.8.33",
        port=2030,  # 默认查询端口
        user="root",
        password="quxing2021",
        database="donggua"
    )

    # 示例1：基本查询
    sql1 = """
    SELECT 
       *
       from live_base limit 10;
    """

    df1 = client.execute_query(sql1)
    print(df1.head())