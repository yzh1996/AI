import pymysql
import os

# ===== 配置区 =====
STARROCKS_CONFIG = {
    'host': '192.168.8.33',
    'port': 2030,
    'user': 'root',
    'password': 'quxing2021',
    'database': 'donggua',
    'charset': 'utf8mb4',
    'autocommit': True
}

# 要导出的表名列表
TABLE_NAMES = [
    "anchor_daily", "anchor_follow_incr", "anchor_video_item_gjz_test", "date_video_data", "jl_user", "live_base","live_product_sale","live_base_view"
    # 可继续添加
]

# 输出文件路径
OUTPUT_FILE = "starrocks_tables_ddl.sql"


# ===================

def get_clean_ddl(table_name: str) -> str:
    """获取纯净的 CREATE TABLE ... ENGINE=OLAP 部分"""
    try:
        conn = pymysql.connect(**STARROCKS_CONFIG)
        with conn.cursor() as cursor:
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            row = cursor.fetchone()
            if not row or len(row) < 2:
                raise ValueError("No DDL returned")

            ddl = row[1]

            # 确保以 ENGINE=OLAP 结尾（去除可能的分号、换行等）
            if ddl.strip().endswith(';'):
                ddl = ddl.strip()[:-1]  # 去掉末尾分号

            # 保证以 ENGINE=OLAP 结尾（StarRocks 标准格式）
            if not ddl.strip().endswith('ENGINE=OLAP'):
                # 如果有 DISTRIBUTED BY / PROPERTIES，也保留（但你的示例没有）
                # 这里按你的需求：只到 ENGINE=OLAP
                lines = ddl.strip().split('\n')
                clean_lines = []
                for line in lines:
                    clean_lines.append(line)
                    if line.strip().startswith(') ENGINE=OLAP'):
                        break
                ddl = '\n'.join(clean_lines)

            return ddl.strip()
    except Exception as e:
        raise RuntimeError(f"Failed to get DDL for '{table_name}': {e}")
    finally:
        if 'conn' in locals():
            conn.close()


def main():
    all_ddls = []

    for table in TABLE_NAMES:
        try:
            ddl = get_clean_ddl(table)
            all_ddls.append(ddl)
            print(f"✅ Fetched DDL for: {table}")
        except Exception as e:
            print(f"❌ Skip table '{table}': {e}")

    # 写入单个文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n\n".join(all_ddls))
        f.write("\n")  # 文件末尾加一个换行

    print(f"\n🎉 所有表的纯净 DDL 已写入: {os.path.abspath(OUTPUT_FILE)}")


if __name__ == "__main__":
    main()