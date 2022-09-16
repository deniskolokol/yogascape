# -*- coding: utf-8 -*-
from datetime import datetime

abbrev = {
    "СН": "Сурья Намаскар",
    "ИС": "Инструктор-стажер",
    "CTC": "Стажерская тестовая серия",
    "ПП": "Перевернутые позиции",
    "АПЖ": "Атлетик: плоский живот"
}

def get_section(section):
    result = []
    for x in section.strip().split(';'):
        for abb, full in abbrev.items():
            x = x.strip().replace(abb, full)
        result.append("- %s" % x)
    return "\n".join(result)

with open('/Users/deko/Documents/dev_web/soma/src/soma/_scripts/2016.11.07-2016.12.31.csv', 'r+') as f:
    for line in f.readlines():
        data = line.split(',')
        dt = datetime.strptime(data[1].strip(), "%d/%m/%Y")
        print("\n", datetime.strftime(dt, "%d/%m/%Y (%a)"))
        print(datetime.strftime(dt.replace(hour=6, minute=0), "%H:%M"))
        print(get_section(data[2]))
        print(datetime.strftime(dt.replace(hour=19, minute=30), "%H:%M"))
        print(get_section(data[3]))
    f.close()
