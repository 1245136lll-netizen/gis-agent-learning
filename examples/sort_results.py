"""第三课示例：使用手工设定的距离练习排序，不执行 GIS 测量。"""


def distance_and_id(record):
    """先按距离排序，距离相同时按 ID 排序。"""
    return (record["distance_m"], record["id"])


def main():
    records = [
        {"id": "demo-b", "name": "教学点乙", "distance_m": 900.0},
        {"id": "demo-c", "name": "教学点丙", "distance_m": 300.0},
        {"id": "demo-a", "name": "教学点甲", "distance_m": 300.0},
    ]
    print("本例距离为手工设定，仅用于练习排序")
    ordered = sorted(records, key=distance_and_id)
    for record in ordered:
        print(f"{record['id']} | {record['name']} | {record['distance_m']:.1f} 米")
    print("原列表的第一项仍是：", records[0]["id"])


if __name__ == "__main__":
    main()
