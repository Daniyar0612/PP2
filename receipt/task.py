import re
import csv
import json

f = open("./raw.txt", "r", encoding="utf-8")
text = f.read()

BINPattern = r"\bБИН\s(?P<BIN>\d+)"
m = re.search(BINPattern, text)
BINResult = m.group("BIN") if m else ""
print(BINResult)

CheckPattern = r"\bЧек\s(?P<Check>№\d+)"
m = re.search(CheckPattern, text)
CheckResult = m.group("Check") if m else ""
print(CheckResult)

DateTimePattern = r"\bВремя:\s*(?P<Date>\d{2}\.\d{2}\.\d{4})\s+(?P<Time>\d{2}:\d{2}:\d{2})"
m = re.search(DateTimePattern, text)
date_str = m.group("Date") if m else ""
time_str = m.group("Time") if m else ""


PaymentPattern = r"^(?P<Method>.+):\s*$"
payment_method = ""
for line in text.splitlines():
    if line.strip().endswith(":") and ("карта" in line.lower() or "налич" in line.lower()):
        payment_method = line.strip().rstrip(":")
        break

AllPricesPattern = r"\b\d{1,3}(?: \d{3})*,\d{2}\b"
all_prices = re.findall(AllPricesPattern, text)

ItemPattern = (
    r"(?P<ItemRowNumber>\d+\.)\n"
    r"(?P<ItemName>.+)\n"
    r"(?P<ItemsCount>[\d, ]+)\s*x\s*(?P<ItemPrice>[\d ,]+)\n"
    r"(?P<TotalItemPrice1>[\d ,]+)\n"
    r"Стоимость\n"
    r"(?P<TotalItemPrice2>[\d ,]+)"
)

prog = re.compile(ItemPattern)
ItemIterator1 = prog.finditer(text)

def money_to_float(s: str) -> float:
    
    return float(s.replace(" ", "").replace(",", "."))

items = []

with open("data.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ItemRowNumber", "ItemName", "ItemsCount", "ItemPrice", "TotalItemPrice"])

    for ItemResult in ItemIterator1:
        row = ItemResult.group("ItemRowNumber").strip()
        name = ItemResult.group("ItemName").strip()
        cnt = ItemResult.group("ItemsCount").strip()
        price = ItemResult.group("ItemPrice").strip()
        total = ItemResult.group("TotalItemPrice2").strip()

        writer.writerow([row, name, cnt, price, total])

        items.append({
            "row": row,
            "name": name,
            "count": cnt,
            "unit_price": price,
            "total": total,
        })

print("###########################")

TotalPattern = r"\bИТОГО:\s*\n(?P<Total>\d{1,3}(?: \d{3})*,\d{2})"
m = re.search(TotalPattern, text)
total_amount = m.group("Total") if m else ""

if total_amount:
    total_amount_value = money_to_float(total_amount)
else:
    total_amount_value = sum(money_to_float(it["total"]) for it in items)

product_names = [it["name"] for it in items]

result = {
    "bin": BINResult,
    "check": CheckResult,
    "datetime": {"date": date_str, "time": time_str},
    "payment_method": payment_method,
    "items": items,
    "total_amount": total_amount if total_amount else f"{total_amount_value:.2f}".replace(".", ","),
    "total_amount_value": total_amount_value
}

print(json.dumps(result, ensure_ascii=False, indent=2))