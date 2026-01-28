import pymysql
import os

# ===== 配置区 =====
DB_CONFIG = {
    'host': '192.168.8.33',
    'port': 2030,
    'user': 'root',
    'password': 'quxing2021',
    'database': 'donggua',
    'charset': 'utf8mb4'
}

# 表名列表（按你的需求修改）
TABLE_NAMES = [
    "live_base_view,jl_user_view"
]

# 输出文件名
OUTPUT_FILE = "table_fields.txt"


# ===================

def get_field_type_list(table_name: str):
    """获取单个表的 (Field, Type) 列表"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute(f"DESC `{table_name}`")
            return [(row[0], row[1]) for row in cursor.fetchall()]
    except Exception as e:
        return [("ERROR", f"Failed to describe table: {e}")]
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for table in TABLE_NAMES:
            f.write(f"=== {table} ===\n")
            fields = get_field_type_list(table)
            for field, dtype in fields:
                f.write(f"{field}\t{dtype}\n")
            f.write("\n")  # 表之间空一行

    print(f"✅ 所有表的字段信息已写入: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    main()