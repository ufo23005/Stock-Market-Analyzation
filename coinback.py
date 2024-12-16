import requests  # 用於發送 HTTP 請求
from datetime import datetime  # 用於處理日期和時間
import pandas as pd  # 用於處理和存儲表格數據
from sqlalchemy import create_engine, text  # 用於連接和執行 MySQL 查詢
from binance.client import Client  # 幣安 API 客戶端
import pymysql  # 用於處理 MySQL 連接

# 配置 MySQL 資料庫連線
db_user = 'root'  # MySQL 使用者名稱
db_password = ''  # MySQL 密碼
db_host = 'localhost'  # MySQL 主機地址
db_port = '3306'  # MySQL 埠
db_name = 'crypto'  # MySQL 資料庫名稱

# Binance API 配置
api_key = 'jcsLzl8FP8tNmV9k4sO2kopdgEdeW6hc5B9CpyyrV5g0ANFQ3njBk2UMLf3vvGVG'  # API 金鑰
api_secret = 'EnSBVh2hwdEAojeSTLi04ikRxfG5FYCmQRMPhzcBv9LQD4Q8a3wFhed1rTmJp5iU'  # API 秘鑰
client = Client(api_key, api_secret)  # 初始化 Binance API 客戶端

# 建立 SQLAlchemy 引擎，用於操作 MySQL 資料庫
engine = create_engine(f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')


def get_first_trade_date_binance(symbol):
    """
    使用幣安 API 查詢某交易對的第一筆交易日期
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 1,
        "startTime": 0
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data:
            first_trade_timestamp = int(data[0][0]) / 1000
            first_trade_date = datetime.utcfromtimestamp(first_trade_timestamp)
            return first_trade_date.strftime("%Y年%m月%d日")
        else:
            return "未找到該交易對的交易記錄"
    
    except requests.exceptions.RequestException as e:
        return f"請求失敗：{e}"


def get_market_data_binance(symbol):
    """
    使用幣安 API 查詢市場數據（24小時價格變動、成交量）
    """
    url = "https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        price_change = data.get("priceChangePercent", "未知")
        volume = data.get("quoteVolume", "未知")
        last_price = data.get("lastPrice", "未知")

        return f"24小時價格變動: {price_change}%, 成交量: ${float(volume):,.2f}, 最新價格: ${float(last_price):,.2f}"
    except requests.exceptions.RequestException as e:
        return f"請求失敗：{e}"


def save_historical_data_to_mysql():
    """
    插入幣安歷史數據到 MySQL 資料庫
    """
    symbol = input("請輸入幣種 (格式：例如 BTCUSDT): ")
    start_date = input("請輸入起始日期 (格式：YYYY-MM-DD): ")
    end_date = input("請輸入結束日期 (格式：YYYY-MM-DD): ")
    interval = Client.KLINE_INTERVAL_1DAY

    table_name = f"{symbol.lower()}_data"

    try:
        klines = client.get_historical_klines(symbol, interval, start_date, end_date)
        print("成功獲取數據！")
    except Exception as e:
        print("無法獲取數據:", e)
        klines = []

    if klines:
        columns = ['日期', '開', '高', '低', '收', '成交量', '關閉時間', '資金流入量', '成交筆數', '主動買入成交量', '主動買入成交金額', '忽略']
        df = pd.DataFrame(klines, columns=columns)
        df.drop(columns=['忽略'], inplace=True)
        df['日期'] = pd.to_datetime(df['日期'], unit='ms')
        df.set_index('日期', inplace=True)
        df[['開', '高', '低', '收', '成交量']] = df[['開', '高', '低', '收', '成交量']].astype(float)
        df['帳跌幅'] = ((df['收'] - df['開']) / df['開']) * 100

        try:
            df.to_sql(name=table_name, con=engine, if_exists='replace', index=True, index_label='日期')
            print(f"{symbol} 的歷史數據已成功存入 MySQL 資料庫的 {table_name} 表格！")
        except Exception as e:
            print("資料存入失敗:", e)
        print(df)
    else:
        print("未獲取到任何歷史數據，請檢查 API 配置和日期範圍。")


def read_historical_data_from_mysql():
    """
    從 MySQL 資料庫讀取歷史數據
    """
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result]
    
    if tables:
        print("\n資料庫中可用的表格如下：")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")

        try:
            choice = int(input("請選擇要讀取的表格（輸入序號）："))
            if 1 <= choice <= len(tables):
                selected_table = tables[choice - 1]
                print(f"您選擇的表格是：{selected_table}")

                query = text(f"SELECT * FROM {selected_table}")
                df = pd.read_sql(query, con=engine)
                print("\n表格中的數據如下：")
                print(df)
            else:
                print("無效選擇，請重新操作。")
        except ValueError:
            print("請輸入有效的數字序號！")
    else:
        print("資料庫中沒有可用的表格。")


def get_top_10_volume_by_date_binance(date):
    """
    根據使用者輸入的日期，查詢當日交易量排名前十的交易對
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        volumes = []
        for item in data:
            volumes.append({
                "symbol": item["symbol"],
                "volume": float(item["quoteVolume"])
            })

        top_10 = sorted(volumes, key=lambda x: x["volume"], reverse=True)[:10]

        print(f"\n在 {date} 當日，交易量排名前十的交易對如下：")
        for rank, item in enumerate(top_10, start=1):
            print(f"{rank}. {item['symbol']} - 成交量: ${item['volume']:,.2f}")
        return top_10

    except requests.exceptions.RequestException as e:
        print(f"請求失敗：{e}")
        return []


def check_large_transactions():
    """
    查詢是否有大額交易，並顯示資金流入或流出及相關交易量資訊
    """
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        large_transaction_threshold = 100_000_000

        large_transactions = []
        for item in data:
            volume = float(item["quoteVolume"])
            price_change = float(item["priceChangePercent"])

            if volume >= large_transaction_threshold:
                direction = "資金流入" if price_change > 0 else "資金流出"
                large_transactions.append({
                    "symbol": item["symbol"],
                    "volume": volume,
                    "direction": direction,
                    "price_change": price_change
                })

        if large_transactions:
            print("\n發現以下大額交易：")
            for rank, tx in enumerate(large_transactions, start=1):
                print(f"{rank}. 交易對: {tx['symbol']}, 成交量: ${tx['volume']:,.2f}, 趨勢: {tx['direction']}, 價格變動: {tx['price_change']}%")
        else:
            print("\n未發現符合條件的大額交易。")

    except requests.exceptions.RequestException as e:
        print(f"請求失敗：{e}")


# 主程式入口
if __name__ == "__main__":
    while True:
        print("\n請選擇要查詢的功能：")
        print("1. 查詢第一筆交易日期")
        print("2. 查詢市場數據（24小時價格變動、成交量）")
        print("3. 插入歷史數據到 MySQL")
        print("4. 讀取歷史數據")
        print("5. 查詢當日交易量排名前十的交易對")
        print("6. 查詢大額交易及資金流動方向")
        print("7. 離開程式")
        choice = input("輸入選項 (1/2/3/4/5/6/7)：").strip()

        if choice == "1":
            symbol = input("請輸入幣安交易對（例如 'BTCUSDT'）：").strip().upper()
            result = get_first_trade_date_binance(symbol)
            print(f"{symbol} 的第一筆交易日期是：{result}")

        elif choice == "2":
            symbol = input("請輸入幣安交易對（例如 'BTCUSDT'）：").strip().upper()
            result = get_market_data_binance(symbol)
            print(f"{symbol} 的市場數據是：{result}")

        elif choice == "3":
            save_historical_data_to_mysql()

        elif choice == "4":
            read_historical_data_from_mysql()

        elif choice == "5":
            date = input("請輸入查詢日期 (格式：YYYY-MM-DD)：").strip()
            get_top_10_volume_by_date_binance(date)

        elif choice == "6":
            check_large_transactions()

        elif choice == "7":
            print("感謝使用，再見不送！")
            break

        else:
            print("無效選項，請重新輸入。")
