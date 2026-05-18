# 预制 mock 收支数据（大学生5月日常开销，和金库 fallback 对得上）
DEFAULT_EXPENSES = {
    "records": [
        {"category": "餐饮", "amount": 18.0, "description": "食堂午饭+酸奶", "type": "expense", "date": "2026-05-18", "created_at": "2026-05-18T12:30:00"},
        {"category": "交通", "amount": 6.0, "description": "地铁去图书馆", "type": "expense", "date": "2026-05-18", "created_at": "2026-05-18T09:00:00"},
        {"category": "餐饮", "amount": 35.0, "description": "和室友吃麻辣烫", "type": "expense", "date": "2026-05-17", "created_at": "2026-05-17T19:00:00"},
        {"category": "餐饮", "amount": 12.0, "description": "食堂早午餐", "type": "expense", "date": "2026-05-17", "created_at": "2026-05-17T11:00:00"},
        {"category": "购物", "amount": 25.0, "description": "买了本理财书", "type": "expense", "date": "2026-05-16", "created_at": "2026-05-16T15:30:00"},
        {"category": "餐饮", "amount": 22.0, "description": "外卖晚饭", "type": "expense", "date": "2026-05-16", "created_at": "2026-05-16T18:30:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-05-16", "created_at": "2026-05-16T12:00:00"},
        {"category": "其他", "amount": 30.0, "description": "话费充值", "type": "expense", "date": "2026-05-15", "created_at": "2026-05-15T14:20:00"},
        {"category": "餐饮", "amount": 28.0, "description": "奶茶+午饭", "type": "expense", "date": "2026-05-15", "created_at": "2026-05-15T12:30:00"},
        {"category": "餐饮", "amount": 78.0, "description": "和同学聚餐AA", "type": "expense", "date": "2026-05-14", "created_at": "2026-05-14T19:30:00"},
        {"category": "交通", "amount": 12.0, "description": "地铁公交", "type": "expense", "date": "2026-05-14", "created_at": "2026-05-14T08:00:00"},
        {"category": "购物", "amount": 18.0, "description": "买了洗面奶", "type": "expense", "date": "2026-05-13", "created_at": "2026-05-13T16:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-05-13", "created_at": "2026-05-13T12:00:00"},
        {"category": "餐饮", "amount": 22.0, "description": "食堂晚饭+水果", "type": "expense", "date": "2026-05-12", "created_at": "2026-05-12T18:00:00"},
        {"category": "购物", "amount": 11.0, "description": "买文具", "type": "expense", "date": "2026-05-12", "created_at": "2026-05-12T10:00:00"},
        {"category": "餐饮", "amount": 45.0, "description": "请室友吃烧烤AA", "type": "expense", "date": "2026-05-11", "created_at": "2026-05-11T20:00:00"},
        {"category": "娱乐", "amount": 30.0, "description": "和朋友看电影", "type": "expense", "date": "2026-05-11", "created_at": "2026-05-11T14:00:00"},
        {"category": "兼职", "amount": 500.0, "description": "家教收入到账", "type": "income", "date": "2026-05-10", "created_at": "2026-05-10T09:00:00"},
        {"category": "餐饮", "amount": 20.0, "description": "食堂午晚饭", "type": "expense", "date": "2026-05-10", "created_at": "2026-05-10T18:00:00"},
        {"category": "交通", "amount": 8.0, "description": "公交去兼职", "type": "expense", "date": "2026-05-10", "created_at": "2026-05-10T07:30:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-05-09", "created_at": "2026-05-09T12:00:00"},
        {"category": "餐饮", "amount": 8.0, "description": "早餐豆浆油条", "type": "expense", "date": "2026-05-09", "created_at": "2026-05-09T07:30:00"},
        {"category": "购物", "amount": 33.0, "description": "日用品补货", "type": "expense", "date": "2026-05-08", "created_at": "2026-05-08T14:00:00"},
        {"category": "餐饮", "amount": 56.0, "description": "请室友吃火锅", "type": "expense", "date": "2026-05-08", "created_at": "2026-05-08T19:00:00"},
        {"category": "餐饮", "amount": 12.0, "description": "早午餐", "type": "expense", "date": "2026-05-07", "created_at": "2026-05-07T10:30:00"},
        {"category": "交通", "amount": 6.0, "description": "坐公交", "type": "expense", "date": "2026-05-07", "created_at": "2026-05-07T08:00:00"},
        {"category": "餐饮", "amount": 26.0, "description": "午饭+下午茶", "type": "expense", "date": "2026-05-06", "created_at": "2026-05-06T15:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂晚饭", "type": "expense", "date": "2026-05-06", "created_at": "2026-05-06T18:00:00"},
        {"category": "购物", "amount": 20.0, "description": "买零食囤货", "type": "expense", "date": "2026-05-05", "created_at": "2026-05-05T15:00:00"},
        {"category": "餐饮", "amount": 38.0, "description": "和同学火锅AA", "type": "expense", "date": "2026-05-05", "created_at": "2026-05-05T19:00:00"},
        {"category": "餐饮", "amount": 25.0, "description": "奶茶+蛋糕", "type": "expense", "date": "2026-05-04", "created_at": "2026-05-04T14:00:00"},
        {"category": "购物", "amount": 88.0, "description": "买了件T恤", "type": "expense", "date": "2026-05-03", "created_at": "2026-05-03T16:00:00"},
        {"category": "餐饮", "amount": 18.0, "description": "食堂午饭", "type": "expense", "date": "2026-05-03", "created_at": "2026-05-03T12:00:00"},
        {"category": "交通", "amount": 12.0, "description": "地铁去市中心", "type": "expense", "date": "2026-05-03", "created_at": "2026-05-03T10:00:00"},
        {"category": "餐饮", "amount": 40.0, "description": "和朋友下午茶", "type": "expense", "date": "2026-05-02", "created_at": "2026-05-02T15:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-05-02", "created_at": "2026-05-02T12:00:00"},
        {"category": "生活费", "amount": 2000.0, "description": "妈妈转了这个月生活费", "type": "income", "date": "2026-05-01", "created_at": "2026-05-01T09:00:00"},
        {"category": "餐饮", "amount": 25.0, "description": "奶茶+午饭", "type": "expense", "date": "2026-05-01", "created_at": "2026-05-01T12:30:00"},
        {"category": "购物", "amount": 20.0, "description": "买纪念品", "type": "expense", "date": "2026-05-01", "created_at": "2026-05-01T17:00:00"},
        # ---- 4月 ----
        {"category": "餐饮", "amount": 32.0, "description": "和室友吃烤鱼AA", "type": "expense", "date": "2026-04-30", "created_at": "2026-04-30T19:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-04-30", "created_at": "2026-04-30T12:00:00"},
        {"category": "交通", "amount": 8.0, "description": "地铁去市区", "type": "expense", "date": "2026-04-28", "created_at": "2026-04-28T09:00:00"},
        {"category": "餐饮", "amount": 22.0, "description": "外卖黄焖鸡", "type": "expense", "date": "2026-04-27", "created_at": "2026-04-27T18:30:00"},
        {"category": "餐饮", "amount": 18.0, "description": "食堂午饭+酸奶", "type": "expense", "date": "2026-04-25", "created_at": "2026-04-25T12:30:00"},
        {"category": "购物", "amount": 45.0, "description": "买防晒霜", "type": "expense", "date": "2026-04-24", "created_at": "2026-04-24T15:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-04-23", "created_at": "2026-04-23T12:00:00"},
        {"category": "餐饮", "amount": 38.0, "description": "奶茶+炸鸡", "type": "expense", "date": "2026-04-22", "created_at": "2026-04-22T16:00:00"},
        {"category": "娱乐", "amount": 55.0, "description": "和朋友密室逃脱", "type": "expense", "date": "2026-04-20", "created_at": "2026-04-20T14:00:00"},
        {"category": "餐饮", "amount": 20.0, "description": "食堂午饭+水果", "type": "expense", "date": "2026-04-18", "created_at": "2026-04-18T12:00:00"},
        {"category": "交通", "amount": 15.0, "description": "打车去火车站", "type": "expense", "date": "2026-04-14", "created_at": "2026-04-14T07:00:00"},
        {"category": "餐饮", "amount": 25.0, "description": "景区吃面+饮料", "type": "expense", "date": "2026-04-05", "created_at": "2026-04-05T12:30:00"},
        {"category": "交通", "amount": 12.0, "description": "清明春游公交", "type": "expense", "date": "2026-04-05", "created_at": "2026-04-05T08:00:00"},
        {"category": "娱乐", "amount": 40.0, "description": "清明踏青门票", "type": "expense", "date": "2026-04-04", "created_at": "2026-04-04T10:00:00"},
        {"category": "餐饮", "amount": 35.0, "description": "春游野餐食材AA", "type": "expense", "date": "2026-04-04", "created_at": "2026-04-04T09:00:00"},
        {"category": "餐饮", "amount": 16.0, "description": "食堂午饭", "type": "expense", "date": "2026-04-03", "created_at": "2026-04-03T12:00:00"},
        {"category": "兼职", "amount": 400.0, "description": "家教工资结算", "type": "income", "date": "2026-04-02", "created_at": "2026-04-02T10:00:00"},
        {"category": "生活费", "amount": 1800.0, "description": "爸爸转了四月生活费", "type": "income", "date": "2026-04-01", "created_at": "2026-04-01T08:30:00"},
        {"category": "餐饮", "amount": 18.0, "description": "食堂午饭", "type": "expense", "date": "2026-04-01", "created_at": "2026-04-01T12:00:00"},
        # ---- 3月 ----
        {"category": "餐饮", "amount": 28.0, "description": "和同学吃串串", "type": "expense", "date": "2026-03-31", "created_at": "2026-03-31T19:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-03-30", "created_at": "2026-03-30T12:00:00"},
        {"category": "交通", "amount": 6.0, "description": "公交去自习室", "type": "expense", "date": "2026-03-28", "created_at": "2026-03-28T08:30:00"},
        {"category": "餐饮", "amount": 20.0, "description": "食堂午晚饭", "type": "expense", "date": "2026-03-27", "created_at": "2026-03-27T18:00:00"},
        {"category": "购物", "amount": 35.0, "description": "买了几支中性笔和笔记本", "type": "expense", "date": "2026-03-25", "created_at": "2026-03-25T14:00:00"},
        {"category": "餐饮", "amount": 22.0, "description": "奶茶+面包", "type": "expense", "date": "2026-03-24", "created_at": "2026-03-24T15:30:00"},
        {"category": "餐饮", "amount": 16.0, "description": "食堂午饭", "type": "expense", "date": "2026-03-22", "created_at": "2026-03-22T12:00:00"},
        {"category": "其他", "amount": 30.0, "description": "话费充值", "type": "expense", "date": "2026-03-20", "created_at": "2026-03-20T10:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-03-19", "created_at": "2026-03-19T12:00:00"},
        {"category": "购物", "amount": 68.0, "description": "开学买教材二手", "type": "expense", "date": "2026-03-05", "created_at": "2026-03-05T10:00:00"},
        {"category": "购物", "amount": 25.0, "description": "文具补货（荧光笔+便签）", "type": "expense", "date": "2026-03-04", "created_at": "2026-03-04T14:00:00"},
        {"category": "餐饮", "amount": 40.0, "description": "开学聚餐AA", "type": "expense", "date": "2026-03-03", "created_at": "2026-03-03T18:30:00"},
        {"category": "交通", "amount": 10.0, "description": "地铁去学校", "type": "expense", "date": "2026-03-03", "created_at": "2026-03-03T08:00:00"},
        {"category": "餐饮", "amount": 18.0, "description": "食堂午饭+豆浆", "type": "expense", "date": "2026-03-02", "created_at": "2026-03-02T12:00:00"},
        {"category": "兼职", "amount": 350.0, "description": "上月家教结算", "type": "income", "date": "2026-03-02", "created_at": "2026-03-02T09:00:00"},
        {"category": "生活费", "amount": 2000.0, "description": "妈妈转了三月生活费", "type": "income", "date": "2026-03-01", "created_at": "2026-03-01T09:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-03-01", "created_at": "2026-03-01T12:00:00"},
        # ---- 2月 ----
        {"category": "餐饮", "amount": 30.0, "description": "和室友聚餐", "type": "expense", "date": "2026-02-28", "created_at": "2026-02-28T19:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-02-27", "created_at": "2026-02-27T12:00:00"},
        {"category": "交通", "amount": 6.0, "description": "公交出门", "type": "expense", "date": "2026-02-25", "created_at": "2026-02-25T09:00:00"},
        {"category": "餐饮", "amount": 18.0, "description": "食堂晚饭+水果", "type": "expense", "date": "2026-02-24", "created_at": "2026-02-24T18:00:00"},
        {"category": "餐饮", "amount": 22.0, "description": "奶茶+小蛋糕", "type": "expense", "date": "2026-02-22", "created_at": "2026-02-22T15:00:00"},
        {"category": "其他", "amount": 30.0, "description": "话费充值", "type": "expense", "date": "2026-02-20", "created_at": "2026-02-20T10:00:00"},
        {"category": "餐饮", "amount": 16.0, "description": "食堂午饭", "type": "expense", "date": "2026-02-19", "created_at": "2026-02-19T12:00:00"},
        {"category": "餐饮", "amount": 65.0, "description": "情人节和对象吃饭", "type": "expense", "date": "2026-02-14", "created_at": "2026-02-14T18:30:00"},
        {"category": "购物", "amount": 120.0, "description": "情人节买礼物", "type": "expense", "date": "2026-02-14", "created_at": "2026-02-14T14:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-02-13", "created_at": "2026-02-13T12:00:00"},
        {"category": "交通", "amount": 8.0, "description": "地铁去商场", "type": "expense", "date": "2026-02-13", "created_at": "2026-02-13T13:30:00"},
        {"category": "餐饮", "amount": 20.0, "description": "食堂午晚饭", "type": "expense", "date": "2026-02-11", "created_at": "2026-02-11T18:00:00"},
        {"category": "购物", "amount": 25.0, "description": "买了双袜子和内衣", "type": "expense", "date": "2026-02-10", "created_at": "2026-02-10T16:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-02-08", "created_at": "2026-02-08T12:00:00"},
        {"category": "兼职", "amount": 300.0, "description": "寒假兼职尾款", "type": "income", "date": "2026-02-05", "created_at": "2026-02-05T10:00:00"},
        {"category": "生活费", "amount": 1500.0, "description": "妈妈转了二月生活费", "type": "income", "date": "2026-02-01", "created_at": "2026-02-01T09:00:00"},
        {"category": "餐饮", "amount": 18.0, "description": "开学第一顿食堂", "type": "expense", "date": "2026-02-01", "created_at": "2026-02-01T12:00:00"},
        # ---- 1月 ----
        {"category": "餐饮", "amount": 35.0, "description": "回家前和室友吃散伙饭", "type": "expense", "date": "2026-01-25", "created_at": "2026-01-25T19:00:00"},
        {"category": "交通", "amount": 15.0, "description": "打车去火车站", "type": "expense", "date": "2026-01-24", "created_at": "2026-01-24T07:30:00"},
        {"category": "购物", "amount": 150.0, "description": "年货带回家（坚果礼盒）", "type": "expense", "date": "2026-01-22", "created_at": "2026-01-22T14:00:00"},
        {"category": "购物", "amount": 80.0, "description": "给爸妈买新年小礼物", "type": "expense", "date": "2026-01-22", "created_at": "2026-01-22T15:30:00"},
        {"category": "餐饮", "amount": 20.0, "description": "食堂午饭+奶茶", "type": "expense", "date": "2026-01-21", "created_at": "2026-01-21T12:30:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-01-20", "created_at": "2026-01-20T12:00:00"},
        {"category": "其他", "amount": 30.0, "description": "话费充值", "type": "expense", "date": "2026-01-18", "created_at": "2026-01-18T10:00:00"},
        {"category": "餐饮", "amount": 18.0, "description": "食堂晚饭", "type": "expense", "date": "2026-01-17", "created_at": "2026-01-17T18:00:00"},
        {"category": "餐饮", "amount": 42.0, "description": "期末复习加餐烧烤", "type": "expense", "date": "2026-01-15", "created_at": "2026-01-15T20:00:00"},
        {"category": "餐饮", "amount": 15.0, "description": "食堂午饭", "type": "expense", "date": "2026-01-14", "created_at": "2026-01-14T12:00:00"},
        {"category": "交通", "amount": 6.0, "description": "公交去图书馆", "type": "expense", "date": "2026-01-13", "created_at": "2026-01-13T08:00:00"},
        {"category": "购物", "amount": 15.0, "description": "打印复习资料", "type": "expense", "date": "2026-01-12", "created_at": "2026-01-12T10:00:00"},
        {"category": "餐饮", "amount": 25.0, "description": "和同学吃麻辣烫", "type": "expense", "date": "2026-01-10", "created_at": "2026-01-10T18:30:00"},
        {"category": "餐饮", "amount": 16.0, "description": "食堂午饭", "type": "expense", "date": "2026-01-08", "created_at": "2026-01-08T12:00:00"},
        {"category": "娱乐", "amount": 30.0, "description": "KTV跨年聚会AA", "type": "expense", "date": "2026-01-01", "created_at": "2026-01-01T22:00:00"},
        {"category": "生活费", "amount": 500.0, "description": "过年爷爷奶奶红包", "type": "income", "date": "2026-01-28", "created_at": "2026-01-28T10:00:00"},
        {"category": "生活费", "amount": 2000.0, "description": "妈妈转了一月生活费", "type": "income", "date": "2026-01-01", "created_at": "2026-01-01T09:00:00"},
    ],
    "monthly_summary": {"total_expense": 1044.0, "total_income": 2500.0}
}

# 预制 mock 金库数据
DEFAULT_VAULT = {
    "total_assets": 13579.30,
    "monthly_growth": 856,
    "accounts": {
        "active_pool": {
            "label": "活期池",
            "balance": 3428.50,
            "rate": "1.8%",
            "principal": 3400.00,
            "monthly_profit": 28.50,
            "products": [
                {"name": "朝朝盈2号", "amount": 2000.00, "buy_date": "2026-03-01", "rate": "1.85%"},
                {"name": "招商活钱管家", "amount": 1000.00, "buy_date": "2026-04-10", "rate": "1.72%"},
                {"name": "零钱宝", "amount": 428.50, "buy_date": "2026-05-05", "rate": "1.65%"}
            ],
            "transactions": [
                {"type": "in", "amount": 428.50, "date": "2026-05-05", "description": "转入零钱宝"},
                {"type": "in", "amount": 1000.00, "date": "2026-04-10", "description": "转入招商活钱管家"},
                {"type": "in", "amount": 2000.00, "date": "2026-03-01", "description": "首次转入朝朝盈2号"}
            ]
        },
        "fixed_deposit": {
            "label": "定期舱",
            "balance": 8000.00,
            "rate": "3.2%",
            "term": "90天",
            "principal": 8000.00,
            "monthly_profit": 64.00,
            "products": [
                {"name": "招银理财90天", "amount": 5000.00, "buy_date": "2026-03-15", "rate": "3.2%", "maturity_date": "2026-06-13"},
                {"name": "招银理财60天", "amount": 3000.00, "buy_date": "2026-04-01", "rate": "3.0%", "maturity_date": "2026-05-31"}
            ],
            "transactions": [
                {"type": "in", "amount": 3000.00, "date": "2026-04-01", "description": "买入招银理财60天"},
                {"type": "in", "amount": 5000.00, "date": "2026-03-15", "description": "买入招银理财90天"}
            ]
        },
        "fund_collection": {
            "label": "基金图鉴",
            "balance": 2150.80,
            "rate": "+2.3%",
            "principal": 2100.00,
            "monthly_profit": 50.80,
            "products": [
                {"name": "沪深300指数A", "amount": 1000.00, "buy_date": "2026-02-20", "rate": "+3.1%", "code": "000300"},
                {"name": "中证500增强", "amount": 600.00, "buy_date": "2026-03-10", "rate": "+1.8%", "code": "000905"},
                {"name": "纯债基金C", "amount": 500.00, "buy_date": "2026-04-05", "rate": "+0.9%", "code": "007531"}
            ],
            "transactions": [
                {"type": "in", "amount": 500.00, "date": "2026-04-05", "description": "定投纯债基金C"},
                {"type": "in", "amount": 600.00, "date": "2026-03-10", "description": "买入中证500增强"},
                {"type": "in", "amount": 1000.00, "date": "2026-02-20", "description": "首次买入沪深300指数A"}
            ]
        }
    },
    "goals": [
        {"name": "AirPods Pro", "target": 1799, "current": 1295, "emoji": "🎧"},
        {"name": "毕业旅行基金", "target": 5000, "current": 2250, "emoji": "✈️"},
        {"name": "新款iPad", "target": 3499, "current": 980, "emoji": "📱"}
    ]
}
