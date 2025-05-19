import os, sys, random, pickle, time, datetime

# ==== UI LIBS ==== #
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.align import Align
    from rich import box
    RICH = True
    console = Console()

except:
    RICH = False

try:
    from pyfiglet import Figlet
    PYF = True
except:
    PYF = False

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA = True
except:
    COLORAMA = False

# ==== WORLD DATA ==== #
MAP_LAYOUT = [
    ["Làng",      "Rừng",     "Hang động"],
    ["Thành phố", "Đồng cỏ",  "Núi tuyết"],
    ["Bờ biển",   "Khu rừng cổ", "Lâu đài"],
    ["Sa mạc lửa",  "Đảo băng",  "Tháp cổ"],
    ["Địa Ngục"],
]
MAP_DESC = {
    "Làng": "Nơi khởi đầu hành trình, bình yên & an toàn.",
    "Rừng": "Khu rừng rậm rạp, nhiều quái vật nhỏ và bí ẩn.",
    "Hang động": "Tối tăm, nguy hiểm, kho báu và quái vật mạnh.",
    "Thành phố": "Nhộn nhịp, nhiều cửa hàng, NPC và sự kiện đặc biệt.",
    "Đồng cỏ": "Thoáng đãng, đôi khi gặp sự kiện hiếm.",
    "Núi tuyết": "Lạnh giá, có quái vật băng giá và boss phụ.",
    "Bờ biển": "Thương nhân, kho báu, nguy hiểm ban đêm.",
    "Khu rừng cổ": "Rất nguy hiểm, nhiều bí ẩn, boss ẩn.",
    "Lâu đài": "Nơi cuối cùng, boss mạnh nhất cư ngụ. Chỉ mở khi đủ điều kiện.",
    "Sa mạc lửa": "Nóng bỏng, quái lửa, boss Rồng Lửa, nhiều bí ẩn cổ đại.",
    "Đảo băng": "Lạnh giá cực độ, boss Hổ Băng, nguy hiểm vào ban đêm.",
    "Tháp cổ": "Tháp bị nguyền rủa, boss Pháp sư cổ đại, nhiều bẫy và kho báu.",
    "Địa ngục": "Nơi nguy hiểm nhất, chỉ mở khi đủ điều kiện, boss cuối thực sự.",
}
AREA_LEVEL_HINT = {
    "Làng": (1, 2), "Rừng": (2, 3), "Hang động": (3, 5), "Thành phố": (2, 4),
    "Đồng cỏ": (2, 4), "Bờ biển": (2, 5), "Núi tuyết": (5, 7), 
    "Sa mạc lửa": (7, 10), "Khu rừng cổ": (7, 8), "Lâu đài": (8, 99), 
    "Đảo băng": (8, 12), "Tháp cổ": (10, 14), "Địa ngục": (15, 99),
}

BASE_CLASSES = {
    "Vô nghề":   {"STR": 2, "DEX": 2, "VIT": 2, "INT": 2, "LUCK": 2, "HP": 18, "MP": 6},
    "Kiếm sĩ":   {"STR": 6, "DEX": 4, "VIT": 5, "INT": 2, "LUCK": 3, "HP": 32, "MP": 10},
    "Pháp sư":   {"STR": 2, "DEX": 3, "VIT": 4, "INT": 8, "LUCK": 4, "HP": 22, "MP": 24},
    "Sát thủ":   {"STR": 4, "DEX": 8, "VIT": 4, "INT": 2, "LUCK": 5, "HP": 26, "MP": 12},
    "Cung thủ":  {"STR": 4, "DEX": 7, "VIT": 4, "INT": 3, "LUCK": 5, "HP": 25, "MP": 11},
    "Võ sư":     {"STR": 7, "DEX": 5, "VIT": 6, "INT": 2, "LUCK": 2, "HP": 34, "MP": 8}
}

ADVANCED_CLASSES = {
    "Kiếm khách":    {"STR": 10, "DEX": 5, "VIT": 9, "INT": 3, "LUCK": 4, "HP": 42, "MP": 14, "base": "Kiếm sĩ"},
    "Pháp sư cấp cao":{"STR": 3, "DEX": 4, "VIT": 5, "INT": 13, "LUCK": 4, "HP": 25, "MP": 38, "base": "Pháp sư"},
    "Sát thủ bóng đêm":{"STR": 7, "DEX": 12, "VIT": 6, "INT": 3, "LUCK": 7, "HP": 30, "MP": 19, "base": "Sát thủ"},
    "Xạ thủ":        {"STR": 6, "DEX": 12, "VIT": 6, "INT": 4, "LUCK": 7, "HP": 28, "MP": 16, "base": "Cung thủ"},
    "Võ tướng":      {"STR": 12, "DEX": 7, "VIT": 10, "INT": 3, "LUCK": 4, "HP": 44, "MP": 12, "base": "Võ sư"},
    "Kiếm thánh":    {"STR": 15, "DEX": 7, "VIT": 12, "INT": 5, "LUCK": 7, "HP": 55, "MP": 22, "base": "Kiếm sĩ", "hidden": True},
    "Pháp thần":     {"STR": 4, "DEX": 6, "VIT": 7, "INT": 20, "LUCK": 7, "HP": 32, "MP": 60, "base": "Pháp sư", "hidden": True},
    "Bóng ma":       {"STR": 10, "DEX": 18, "VIT": 8, "INT": 5, "LUCK": 10, "HP": 36, "MP": 30, "base": "Sát thủ", "hidden": True},
    "Thợ săn huyền thoại": {"STR": 9, "DEX": 18, "VIT": 8, "INT": 7, "LUCK": 10, "HP": 34, "MP": 26, "base": "Cung thủ", "hidden": True},
    "Quyền vương":   {"STR": 18, "DEX": 10, "VIT": 16, "INT": 4, "LUCK": 6, "HP": 62, "MP": 18, "base": "Võ sư", "hidden": True}
}

CLASS_SKILLS = {
    "Vô nghề": [],
    "Kiếm sĩ": ["Chém nhanh", "Phòng ngự"],
    "Pháp sư": ["Quả cầu lửa", "Khiên phép"],
    "Sát thủ": ["Đâm lén", "Tàng hình"],
    "Cung thủ": ["Bắn 3 mũi", "Bẫy dây"],
    "Võ sư": ["Liên hoàn cước", "Hộ thể"],
    "Kiếm khách": ["Chém xoáy", "Kiếm khí"],
    "Pháp sư cấp cao": ["Lốc xoáy lửa", "Kháng phép"],
    "Sát thủ bóng đêm": ["Cú đâm chí mạng", "Ẩn thân"],
    "Xạ thủ": ["Bão tên", "Bẫy độc"],
    "Võ tướng": ["Cú đấm sấm sét", "Bất khuất"],
    "Kiếm thánh": ["Thánh kiếm", "Bất khả chiến bại"],
    "Pháp thần": ["Thiên hỏa", "Hồi sinh"],
    "Bóng ma": ["Ảo ảnh", "Đoạt mệnh"],
    "Thợ săn huyền thoại": ["Mũi tên thần", "Ẩn thân vô hình"],
    "Quyền vương": ["Tuyệt kỹ quyền vương", "Cường hóa"],
}

SKILL_TREE = {
    "Vô nghề": {
        "Tập luyện": {"level": 1, "desc": "Tăng nhẹ chỉ số ngẫu nhiên.", "next": None},
    },
    "Kiếm sĩ": {
        "Chém nhanh": {"level": 1, "desc": "Tấn công nhanh, sát thương nhỏ.", "next": "Chém xoáy"},
        "Chém xoáy": {"level": 3, "desc": "Tấn công nhiều mục tiêu.", "next": "Phòng ngự"},
        "Phòng ngự": {"level": 5, "desc": "Tăng phòng thủ lượt này.", "next": "Thánh kiếm"},
        "Thánh kiếm": {"level": 8, "desc": "Tuyệt kỹ mạnh nhất.", "next": None},
    },
    "Pháp sư": {
        "Quả cầu lửa": {"level": 1, "desc": "Gây sát thương phép lửa.", "next": "Khiên phép"},
        "Khiên phép": {"level": 2, "desc": "Tạo khiên bảo vệ bản thân.", "next": "Lốc xoáy lửa"},
        "Lốc xoáy lửa": {"level": 4, "desc": "Sát thương diện rộng.", "next": "Thiên hỏa"},
        "Thiên hỏa": {"level": 8, "desc": "Chiêu thức cực mạnh.", "next": None},
    },
    "Sát thủ": {
        "Đâm lén": {"level": 1, "desc": "Tấn công chí mạng.", "next": "Tàng hình"},
        "Tàng hình": {"level": 2, "desc": "Tránh đòn lượt sau.", "next": "Cú đâm chí mạng"},
        "Cú đâm chí mạng": {"level": 5, "desc": "Sát thương cực lớn lên mục tiêu yếu máu.", "next": None},
    },
    "Cung thủ": {
        "Bắn 3 mũi": {"level": 1, "desc": "Bắn nhiều mũi tên cùng lúc.", "next": "Bẫy dây"},
        "Bẫy dây": {"level": 3, "desc": "Đặt bẫy, giảm tốc quái.", "next": "Bão tên"},
        "Bão tên": {"level": 6, "desc": "Tấn công diện rộng.", "next": None},
    },
    "Võ sư": {
        "Liên hoàn cước": {"level": 1, "desc": "Đá liên tiếp.", "next": "Hộ thể"},
        "Hộ thể": {"level": 2, "desc": "Tăng phòng thủ tạm thời.", "next": "Cú đấm sấm sét"},
        "Cú đấm sấm sét": {"level": 6, "desc": "Sát thương mạnh, có thể làm choáng.", "next": None},
    },
    "Kiếm khách": {
        "Chém xoáy": {"level": 1, "desc": "Kỹ năng nâng cao của kiếm.", "next": "Kiếm khí"},
        "Kiếm khí": {"level": 4, "desc": "Tấn công xuyên giáp.", "next": None},
    },
    "Pháp sư cấp cao": {
        "Lốc xoáy lửa": {"level": 1, "desc": "Sát thương phép diện rộng.", "next": "Kháng phép"},
        "Kháng phép": {"level": 5, "desc": "Giảm sát thương phép nhận vào.", "next": None},
    },
    "Sát thủ bóng đêm": {
        "Cú đâm chí mạng": {"level": 1, "desc": "Tăng mạnh sát thương chí mạng.", "next": "Ẩn thân"},
        "Ẩn thân": {"level": 4, "desc": "Tránh toàn bộ đòn 1 lượt.", "next": None},
    },
    "Xạ thủ": {
        "Bão tên": {"level": 1, "desc": "Tấn công diện rộng.", "next": "Bẫy độc"},
        "Bẫy độc": {"level": 5, "desc": "Bẫy gây độc cho đối thủ.", "next": None},
    },
    "Võ tướng": {
        "Cú đấm sấm sét": {"level": 1, "desc": "Đánh choáng diện rộng.", "next": "Bất khuất"},
        "Bất khuất": {"level": 4, "desc": "Miễn nhiễm sát thương 1 lượt.", "next": None},
    },
    "Kiếm thánh": {
        "Thánh kiếm": {"level": 1, "desc": "Chiêu kiếm tối thượng.", "next": "Bất khả chiến bại"},
        "Bất khả chiến bại": {"level": 8, "desc": "Không thể bị hạ gục 1 lần.", "next": None},
    },
    "Pháp thần": {
        "Thiên hỏa": {"level": 1, "desc": "Thiên thạch cực mạnh.", "next": "Hồi sinh"},
        "Hồi sinh": {"level": 8, "desc": "Hồi sinh khi tử trận.", "next": None},
    },
    "Bóng ma": {
        "Ảo ảnh": {"level": 1, "desc": "Giảm sát thương nhận vào.", "next": "Đoạt mệnh"},
        "Đoạt mệnh": {"level": 8, "desc": "Tấn công hút máu.", "next": None},
    },
    "Thợ săn huyền thoại": {
        "Mũi tên thần": {"level": 1, "desc": "Mũi tên sát thương cực mạnh.", "next": "Ẩn thân vô hình"},
        "Ẩn thân vô hình": {"level": 5, "desc": "Vô hình 2 lượt.", "next": None},
    },
    "Quyền vương": {
        "Tuyệt kỹ quyền vương": {"level": 1, "desc": "Sát thương diện rộng cực mạnh.", "next": "Cường hóa"},
        "Cường hóa": {"level": 7, "desc": "Tăng mạnh chỉ số bản thân.", "next": None},
    },
}


ITEM_DATABASE = {
    "Kiếm sắt": {"type": "vũ khí", "STR": 2, "desc": "Tăng 2 sức mạnh (Kiếm sĩ/Kiếm khách/Kiếm thánh)", "quality": "thường", "class": ["Kiếm sĩ","Kiếm khách","Kiếm thánh"]},
    "Gậy phép": {"type": "vũ khí", "INT": 3, "desc": "Tăng 3 trí tuệ (Pháp sư)", "quality": "thường", "class": ["Pháp sư","Pháp sư cấp cao","Pháp thần"]},
    "Dao găm": {"type": "vũ khí", "DEX": 2, "desc": "Tăng 2 nhanh nhẹn (Sát thủ)", "quality": "thường", "class": ["Sát thủ","Sát thủ bóng đêm","Bóng ma"]},
    "Cung gỗ": {"type": "vũ khí", "DEX": 2, "desc": "Tăng 2 nhanh nhẹn (Cung thủ)", "quality": "thường", "class": ["Cung thủ", "Xạ thủ", "Thợ săn huyền thoại"]},
    "Găng tập": {"type": "vũ khí", "STR": 1, "DEX": 1, "desc": "Tăng 1 sức mạnh, 1 nhanh nhẹn (Võ sư)", "quality": "thường", "class": ["Võ sư","Võ tướng","Quyền vương"]},
    "Kiếm truyền thuyết": {"type": "vũ khí", "STR": 6, "desc": "Vũ khí cực mạnh! (Kiếm sĩ/Kiếm khách/Kiếm thánh)", "quality": "siêu hiếm", "class": ["Kiếm sĩ","Kiếm khách","Kiếm thánh"]},
    "Trượng cổ đại": {"type": "vũ khí", "INT": 8, "desc": "Tăng 8 INT cho pháp sư", "quality": "hiếm", "class": ["Pháp sư","Pháp sư cấp cao","Pháp thần"]},
    "Áo giáp nhẹ": {"type": "áo giáp", "VIT": 2, "desc": "Tăng 2 thể chất", "quality": "thường"},
    "Nhẫn may mắn": {"type": "nhẫn", "LUCK": 2, "desc": "Tăng 2 may mắn", "quality": "hiếm"},
    "Thuốc máu": {"type": "thuốc", "HP": 20, "desc": "Hồi phục 20 HP"},
    "Thuốc mana": {"type": "thuốc", "MP": 15, "desc": "Hồi phục 15 MP"},
    "Mảnh phép bí ẩn": {"type": "chế", "desc": "Dùng để chế tạo vật phẩm cực mạnh", "quality": "siêu hiếm"},
    "Kiếm Rồng Lửa": {"type": "vũ khí", "STR": 12, "desc": "Vũ khí truyền thuyết, chỉ dành cho Kiếm thánh/Quyền vương. Kèm hiệu ứng đốt cháy.", "quality": "truyền thuyết", "class": ["Kiếm thánh", "Quyền vương"]},
    "Vuốt Băng Truyền Thuyết": {"type": "vũ khí", "DEX": 10, "desc": "Vũ khí truyền thuyết tăng DEX, có thể đóng băng kẻ địch.", "quality": "truyền thuyết", "class": ["Sát thủ bóng đêm", "Thợ săn huyền thoại"]},
    "Trượng Cổ Truyền": {"type": "vũ khí", "INT": 15, "desc": "Trượng pháp sư truyền thuyết, tăng INT, mở khóa kỹ năng cổ đại.", "quality": "truyền thuyết", "class": ["Pháp thần"]},
    "Vương Miện Địa Ngục": {"type": "nhẫn", "LUCK": 8, "desc": "Tăng vận may cực mạnh, chỉ rơi ra từ boss cuối Địa ngục.", "quality": "truyền thuyết"},
    "Nhẫn Lửa Truyền Thuyết": {"type": "nhẫn", "LUCK": 5, "desc": "Nhẫn truyền thuyết, tăng may mắn và kháng lửa.", "quality": "truyền thuyết"},
    "Áo Choàng Băng": {"type": "áo giáp", "VIT": 8, "desc": "Áo choàng truyền thuyết, tăng VIT, kháng băng.", "quality": "truyền thuyết"},
    "Kiếm Địa Ngục": {"type": "vũ khí", "STR": 20, "desc": "Kiếm mạnh nhất, chỉ dành cho class ẩn, có hiệu ứng đặc biệt.", "quality": "truyền thuyết", "class": ["Bóng ma", "Quyền vương"]},
}

MONSTER_DATABASE = {
    "Slime": {"HP": 18, "MP": 0, "STR": 3, "DEX": 2, "VIT": 2, "EXP": 8, "Gold": 5, "drops": ["Thuốc máu"]},
    "Goblin": {"HP": 22, "MP": 2, "STR": 4, "DEX": 3, "VIT": 3, "EXP": 12, "Gold": 7, "drops": ["Kiếm sắt", "Thuốc máu"]},
    "Drake": {"HP": 36, "MP": 0, "STR": 7, "DEX": 5, "VIT": 5, "EXP": 25, "Gold": 15, "drops": ["Cung gỗ", "Nhẫn may mắn"]},
    "Yeti": {"HP": 45, "MP": 0, "STR": 8, "DEX": 3, "VIT": 8, "EXP": 35, "Gold": 21, "drops": ["Áo giáp nhẹ", "Thuốc máu"]},
    "Dark Lord": {"HP": 110, "MP": 35, "STR": 18, "DEX": 9, "VIT": 13, "EXP": 140, "Gold": 100, "drops": ["Mảnh phép bí ẩn"]},
    "Rồng Lửa": {"HP": 140, "MP": 40, "STR": 24, "DEX": 14, "VIT": 16, "EXP": 250, "Gold": 250, "drops": ["Kiếm Rồng Lửa", "Pet Rồng Lửa", "Nhẫn Lửa Truyền Thuyết"]},
    "Hổ Băng":  {"HP": 120, "MP": 30, "STR": 20, "DEX": 18, "VIT": 15, "EXP": 210, "Gold": 200, "drops": ["Vuốt Băng Truyền Thuyết", "Pet Hổ Băng", "Áo Choàng Băng"]},
    "Pháp sư cổ đại": {"HP": 160, "MP": 80, "STR": 10, "DEX": 10, "VIT": 20, "INT": 30, "EXP": 340, "Gold": 350, "drops": ["Trượng Cổ Truyền", "Nhẫn Pháp Sư Truyền Thuyết"]},
    "Quỷ vương": {"HP": 300, "MP": 120, "STR": 32, "DEX": 18, "VIT": 30, "INT": 24, "EXP": 999, "Gold": 999, "drops": ["Pet Quỷ Vương", "Vương Miện Địa Ngục", "Kiếm Địa Ngục"]},
    "Salamander": {"HP": 42, "MP": 5, "STR": 11, "DEX": 7, "VIT": 7, "EXP": 38, "Gold": 18, "drops": ["Thuốc máu", "Nhẫn Lửa"]},
    "Băng Hồn": {"HP": 38, "MP": 8, "STR": 9, "DEX": 13, "VIT": 7, "EXP": 33, "Gold": 19, "drops": ["Thuốc mana", "Nhẫn Băng"]},
}

AREA_MONSTERS = {
    "Làng": ["Slime"],
    "Rừng": ["Slime", "Goblin"],
    "Hang động": ["Goblin", "Drake"],
    "Thành phố": ["Goblin"],
    "Đồng cỏ": ["Slime", "Goblin"],
    "Núi tuyết": ["Yeti"],
    "Bờ biển": ["Drake"],
    "Khu rừng cổ": ["Drake"],
    "Lâu đài": ["Dark Lord"],
    "Sa mạc lửa": ["Salamander"],
    "Đảo băng": ["Băng Hồn", "Yeti"],
    "Tháp cổ": ["Pháp sư cổ đại"],
    "Địa Ngục": ["Quỷ vương"],
}

PET_DATABASE = {
    "Slime": {"hp": 24, "atk": 4, "skill": "Múc dính"},
    "Drake": {"hp": 40, "atk": 8, "skill": "Lửa phun"},
    "Yeti": {"hp": 50, "atk": 12, "skill": "Gầm băng giá"},
    "Rồng Lửa": {"hp": 85, "atk": 22, "skill": "Hỏa Long Trảo"},
    "Hổ Băng": {"hp": 70, "atk": 19, "skill": "Băng Sát"},
    "Quỷ Vương": {"hp": 110, "atk": 35, "skill": "Địa Ngục Hủy Diệt"},
}

QUEST_DATABASE = [
    {
        "id": 1,
        "name": "Khởi đầu",
        "desc": "Đánh bại 2 Slime ở Rừng.",
        "requirements": {"kill": {"Slime": 2}, "place": "Rừng"},
        "reward_exp": 30,
        "reward_gold": 15,
        "completed": False
    },
    {
        "id": 2,
        "name": "Kho báu hang động",
        "desc": "Tìm kho báu trong Hang động.",
        "requirements": {"event": "kho_bau", "place": "Hang động"},
        "reward_exp": 50,
        "reward_gold": 30,
        "completed": False
    },
    {
        "id": 3,
        "name": "Boss băng giá",
        "desc": "Hạ gục Yeti ở Núi tuyết.",
        "requirements": {"kill": {"Yeti": 1}, "place": "Núi tuyết"},
        "reward_exp": 80,
        "reward_gold": 40,
        "completed": False
    },
    {
        "id": 4,
        "name": "Chế tạo truyền thuyết",
        "desc": "Chế tạo vật phẩm từ Mảnh phép bí ẩn.",
        "requirements": {"craft": "Mảnh phép bí ẩn"},
        "reward_exp": 120,
        "reward_gold": 100,
        "completed": False
    }
]
ACHIEVE_LIST = [
    {"name": "Đánh bại boss cuối", "desc": "Đánh bại Dark Lord ở Lâu đài.", "condition": "boss_final"},
    {"name": "Sưu tầm pet", "desc": "Bắt được đủ 3 loại pet.", "condition": "all_pets"},
    {"name": "Vua kho báu", "desc": "Tìm tối thiểu 5 kho báu.", "condition": "treasure_hunter"},
    {"name": "Chuyển chức class ẩn", "desc": "Khám phá và chuyển chức thành công class ẩn.", "condition": "secret_class"}
]
EVENTS = [
    {"name": "kho_bau", "desc": "Bạn tìm thấy một rương kho báu!", "reward": "random_item"},
    {"name": "phuc_hoi", "desc": "Bạn nghỉ ngơi và được phục hồi hoàn toàn!", "reward": "full_heal"},
    {"name": "thuong_nhan", "desc": "Thương nhân bí ẩn xuất hiện, bạn có thể mua vật phẩm hiếm!", "reward": "shop"},
    {"name": "mini_game", "desc": "Bạn gặp một thử thách nhỏ!", "reward": "mini_game"},
    {"name": "bay", "desc": "Bạn dính bẫy! Mất máu!", "reward": "trap"},
    {"name": "npc_an", "desc": "Bạn gặp NPC bí ẩn, nhận lời khuyên hoặc quà tặng.", "reward": "npc_an"},
    {"name": "nghi_le_chuyen_sinh", "desc": "Nghi lễ chuyển chức bắt đầu! Một thử thách sinh tử đang chờ bạn...", "reward": "jobchange"}
]
PLOT_TWISTS = [
    "Thật ra Dark Lord từng là một anh hùng thất bại.",
    "Có thể thuần hóa Yeti làm pet nếu bạn may mắn.",
    "Nếu đủ kho báu + có Mảnh phép bí ẩn, bạn sẽ mở khóa class ẩn!"
]
MAIN_STORY = [
    "Bạn là người được chọn để cứu lấy thế giới khỏi bóng tối.",
    "Nhiều anh hùng đã thất bại trước khi bạn đến.",
    "Liệu bạn có thể phá vỡ vận mệnh, trở thành huyền thoại chăng?"
]

# ==== UI & TOOL ==== #
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def color(text, col):
    if not COLORAMA: return str(text)
    d = {"red": Fore.RED, "green": Fore.GREEN, "yellow": Fore.YELLOW, "cyan": Fore.CYAN, "magenta": Fore.MAGENTA, "blue": Fore.BLUE, "white": Fore.WHITE}
    return d.get(col, Fore.WHITE) + str(text) + Style.RESET_ALL

def big_title(txt):
    clear_screen()
    if PYF:
        f = Figlet(font="slant")
        t = f.renderText(txt)
        if RICH:
            console.print(Align.center(Panel.fit(t, style="magenta", box=box.DOUBLE, title="🎮 HÀNH TRÌNH ANH HÙNG 🎮")))
        else:
            print(color(t, "magenta"))
    else:
        art = f"=== {txt} ==="
        if RICH:
            console.print(Align.center(Panel.fit(art, style="magenta", box=box.DOUBLE, title="🎮 HÀNH TRÌNH ANH HÙNG 🎮")))
        else:
            print(color(art, "magenta"))

def rich_panel(txt, title="", style="cyan", center=True):
    if RICH:
        panel = Panel.fit(txt, title=title, style=style, box=box.ROUNDED)
        if center: panel = Align.center(panel)
        console.print(panel)
    else:
        print(color(f"== {title} ==\n{txt}", style))

def wait_enter():
    input(color("Nhấn Enter để tiếp tục...", "yellow"))

def show_ascii(name, is_hero=False):
    HERO = r'''
   O
  /|\
  / \
'''
    SLIME = r"""
   __
 _(  )_
(_    _)
  (__)
"""
    DRAKE = r"""
    / \__
   (    @\___
   /         O
  /   (_____/
 /_____/   U
"""
    YETI = r"""
   (    )
  (o  o)
   |  |
  (====)
  //  \\
"""
    DARKLORD = r"""
  /####\
 |      |
 | O  O |
 |  ∆   |
 |______|
"""
    dic = {"Hero": HERO, "Slime": SLIME, "Drake": DRAKE, "Yeti": YETI, "Dark Lord": DARKLORD}
    art = dic.get(name, HERO)
    if RICH:
        console.print(Align.center(Panel(art, title=name, style="yellow" if is_hero else "green")))
    else:
        print(color(art, "yellow" if is_hero else "green"))

def show_status(hero, pet=None, daynight="Ngày"):
    if RICH:
        table = Table(title=f"Trạng thái ({daynight})", box=box.ROUNDED, style="bold cyan", show_lines=True, title_style="bold green")
        table.add_column("Tên", style="bold")
        table.add_column("Class", style="bold magenta")
        table.add_column("Level", style="yellow")
        table.add_column("HP", style="green")
        table.add_column("MP", style="blue")
        table.add_column("Vàng", style="yellow")
        table.add_row(hero.name, hero.char_class, str(hero.level),
                    f"{hero.hp}/{hero.max_hp}", f"{hero.mp}/{hero.max_mp}", str(hero.gold))
        console.print(Align.center(table))
        if pet:
            console.print(Align.center(Panel(f"[bold green]{pet.name}[/bold green] | HP: {pet.hp}/{pet.max_hp}",
                                title="Pet", style="green")))
    else:
        print(color(f"{hero.name} [{hero.char_class}] Lvl:{hero.level} HP:{hero.hp}/{hero.max_hp} MP:{hero.mp}/{hero.max_mp} Vàng:{hero.gold}", "cyan"))
        if pet:
            print(color(f"Đồng hành: {pet.name} | HP:{pet.hp}/{pet.max_hp}", "green"))

def show_map(hero):
    if RICH:
        table = Table(title="🗺️  BẢN ĐỒ THẾ GIỚI", box=box.HEAVY_EDGE, style="bold blue")
        for _ in range(len(MAP_LAYOUT[0])): table.add_column()
        for i, row in enumerate(MAP_LAYOUT):
            cells = []
            for j, loc in enumerate(row):
                marker = "[*]" if hero.map_x == i and hero.map_y == j else "   "
                lv = ""
                if loc:
                    lvmin, lvmax = AREA_LEVEL_HINT.get(loc, (1, 1))
                    lv = f"(Lv {lvmin}-{lvmax})"
                cell = f"{marker} {loc} {lv}" if loc else ""
                cells.append(cell)
            table.add_row(*cells)
        console.print(Align.center(table))
    else:
        print(color("BẢN ĐỒ:", "cyan"))
        for i, row in enumerate(MAP_LAYOUT):
            for j, loc in enumerate(row):
                if not loc: continue
                marker = "[*]" if hero.map_x == i and hero.map_y == j else "   "
                lvmin, lvmax = AREA_LEVEL_HINT.get(loc, (1, 1))
                lv = f"(Lv {lvmin}-{lvmax})"
                print(f"{marker} {loc} {lv}", end="\t")
            print()
    loc = MAP_LAYOUT[hero.map_x][hero.map_y]
    lvmin, lvmax = AREA_LEVEL_HINT.get(loc, (1, 1))
    print(color(f"Địa điểm: {loc} (Lv {lvmin}-{lvmax}) - {MAP_DESC[loc]}", "yellow"))
    if hasattr(hero, "level") and hero.level < lvmin:
        print(color(f"Cảnh báo: Khu vực này đề xuất level từ {lvmin}. Bạn nên cẩn thận!", "red"))

def show_quest_progress(quests):
    if RICH:
        table = Table(title="📜  NHIỆM VỤ", box=box.ROUNDED, style="bold magenta")
        table.add_column("Tên", style="bold yellow")
        table.add_column("Mô tả", style="")
        table.add_column("Trạng thái", style="yellow")
        for q in quests:
            st = "[HOÀN THÀNH]" if q["completed"] else ""
            table.add_row(q["name"], q["desc"], st)
        console.print(Align.center(table))
    else:
        print("NHIỆM VỤ:")
        for q in quests:
            st = "[X]" if q["completed"] else "[ ]"
            print(f"{st} {q['name']}: {q['desc']}")

def show_help():
    lines = [
        "[bold cyan]=== HƯỚNG DẪN CHƠI GAME ===[/bold cyan]",
        "- Bạn sẽ vào vai anh hùng phiêu lưu qua các vùng đất, đánh quái, nhận nhiệm vụ và khám phá bí mật!",
        "",
        "[bold yellow]1. Kiếm tiền:[/bold yellow] Đánh quái vật, hoàn thành nhiệm vụ, hoặc gặp NPC/mini-game, bạn sẽ nhận được vàng.",
        "[bold yellow]2. Pet (đồng hành):[/bold yellow] Có thể bắt pet ở menu Pet (số lượng tối đa 3 loại). Pet hỗ trợ bạn khi chiến đấu.",
        "[bold yellow]3. Nâng cấp và chuyển nghề:[/bold yellow] Khi đủ level 20 (hoặc đủ điều kiện bí mật), đến Làng để chuyển nghề.",
        "[bold yellow]4. Trang bị & vật phẩm:[/bold yellow] Trang bị giúp tăng chỉ số. Vật phẩm hồi máu/mana dùng trong trận hoặc ngoài trận.",
        "[bold yellow]5. Kỹ năng:[/bold yellow] Mỗi class có bộ kỹ năng riêng. Chọn kỹ năng khi chiến đấu để tối ưu sức mạnh.",
        "[bold yellow]6. Nhiệm vụ & thành tựu:[/bold yellow] Làm nhiệm vụ để nhận exp/vàng, đạt thành tựu để mở khóa nội dung đặc biệt.",
        "[bold yellow]7. Cửa hàng:[/bold yellow] Gặp thương nhân hoặc vào mục cửa hàng để mua vật phẩm hữu ích.",
        "[bold yellow]8. Chế tạo:[/bold yellow] Thu thập nguyên liệu để chế tạo trang bị mạnh mẽ, kể cả vũ khí truyền thuyết!",
        "",
        "[bold green]Mẹo:[/bold green] Hãy thử khám phá thật nhiều, mỗi vùng đất đều có bí mật, sự kiện và bất ngờ chờ đón bạn!",
        "",
        "Chúc bạn trở thành huyền thoại!"
    ]
    for line in lines:
        rich_panel(line, style="cyan")
        time.sleep(0.2)
    wait_enter()

def main_menu():
    if RICH:
        options = [
            ("🌟 Bắt đầu game mới", "new"),
            ("💾 Tiếp tục game", "continue"),
            ("📖 Đọc cốt truyện", "lore"),
            ("🌀 Plot twist/lore ẩn", "twist"),
            ("📚 Hướng dẫn", "help"),
            ("📝 Credits", "credit"),
            ("❌ Thoát", "exit")
        ]
        table = Table(title="MENU CHÍNH", box=box.ROUNDED, style="bold blue")
        table.add_column("STT", style="bold yellow")
        table.add_column("Chức năng", style="bold")
        for i, (desc, _) in enumerate(options):
            table.add_row(str(i+1), desc)
        console.print(Align.center(table))
    else:
        print("1. Bắt đầu game mới\n2. Tiếp tục game\n3. Đọc cốt truyện\n4. Plot twist/Lore ẩn\n5. Hướng dẫn\n6. Credits\n7. Thoát")
    while True:
        c = input("Chọn số: ")
        if c in "1234567":
            return ["new", "continue", "lore", "twist", "help", "credit", "exit"][int(c)-1]
        print(color("Chọn lại!", "red"))

def show_cutscene(key):
    scenes = {
        "intro": """
[bold cyan]
Bạn tỉnh dậy ở một vùng đất xa lạ, ký ức mờ nhạt về thân phận.
Đây là thế giới của những cuộc phiêu lưu, nơi số phận chờ bạn viết nên câu chuyện của chính mình...
[/bold cyan]
        """,
        "ending_good": """
[bold green]
Ánh sáng đã trở lại! Bạn đã trở thành huyền thoại.
[/bold green]
        """,
        "ending_bad": """
[bold red]
Bóng tối nuốt trọn tất cả. Bạn thất bại...
[/bold red]
        """,
        "ending_secret": """
[bold magenta]
Kết thúc bí mật! Bạn đã giải phóng sức mạnh bóng tối, trở thành truyền thuyết sống mãi trong đêm đen...
[/bold magenta]
        """
    }
    t = scenes.get(key, "")
    rich_panel(t, title="Cốt truyện", style="cyan")
    time.sleep(1)
    wait_enter()

def show_lore():
    print(color("=== CỐT TRUYỆN CHÍNH ===", "magenta"))
    for i, line in enumerate(MAIN_STORY):
        rich_panel(line, title=f"Chương {i+1}", style="cyan")
        time.sleep(0.8)
    wait_enter()

def show_twist():
    print(color("=== PLOT TWIST/Lore ẩn ===", "magenta"))
    for t in PLOT_TWISTS:
        rich_panel(t, style="magenta")
        time.sleep(1)
    wait_enter()

def show_credits():
    rich_panel("Game by kazuo2003 & Copilot AI\nASCII Art, Rich UI, Pyfiglet, Python 3", title="Credits", style="magenta")
    wait_enter()

def show_achievements(ach):
    if RICH:
        table = Table(title="🏅  THÀNH TỰU", box=box.HEAVY_EDGE, style="bold green")
        table.add_column("Tên", style="bold yellow")
        table.add_column("Mô tả", style="white")
        table.add_column("Trạng thái", style="magenta")
        for a in ACHIEVE_LIST:
            st = "[Đã đạt]" if a["condition"] in ach else ""
            table.add_row(a["name"], a["desc"], st)
        console.print(Align.center(table))
    else:
        print("THÀNH TỰU:")
        for a in ACHIEVE_LIST:
            st = "[X]" if a["condition"] in ach else ""
            print(f"{st} {a['name']}: {a['desc']}")
    wait_enter()

def transition_effect(loc):
    if RICH:
        dots = "... ..."
        for _ in range(2):
            console.print(Align.center(dots), style="cyan")
            time.sleep(0.2)
            dots += " ..."
        panel = Panel.fit(f"Đã đến: [yellow bold]{loc}[/yellow bold]\n{MAP_DESC[loc]}", style="cyan", title="Chuyển vùng")
        console.print(Align.center(panel))
        time.sleep(0.7)
    else:
        print(color(f"Đang di chuyển đến {loc}...", "cyan"))
        time.sleep(0.6)
        print(color(f"Bạn đã đến {loc}: {MAP_DESC[loc]}", "yellow"))
        time.sleep(0.5)

# ==== GAME LOGIC ==== #
class Hero:
    def __init__(self, name, baseclass):
        base = BASE_CLASSES[baseclass]
        self.name = name
        self.char_class = baseclass
        self.level = 1
        self.exp = 0
        self.gold = 20
        self.skill_points = 0
        self.unlocked_skills = []
        self.stats = dict(base)
        self.max_hp = base["HP"]
        self.hp = self.max_hp
        self.max_mp = base["MP"]
        self.mp = self.max_mp
        self.inventory = ["Thuốc máu", "Thuốc máu", "Thuốc máu"]
        self.equipment = {"vũ khí": None, "áo giáp": None, "nhẫn": None}
        self.skills = CLASS_SKILLS.get(baseclass, [])[:]
        self.map_x, self.map_y = 0, 0
        self.craft_count = 0
        self.treasure_count = 0
        self.pets = []
        self.steps = 0
        self.job_unlocked = False
        self.job_changed = False
        self.job_secret = False
        self.base_class = baseclass
        self.sub_class = None

    def show(self, pet=None, daynight="Ngày"):
        show_status(self, pet, daynight)
        show_ascii(self.char_class if self.char_class in ["Kiếm sĩ","Pháp sư","Sát thủ","Cung thủ","Võ sư"] else "Hero", is_hero=True)
        show_map(self)
    def equip(self, item):
        it = ITEM_DATABASE[item]
        if it["type"] == "vũ khí":
            if self.char_class not in it.get("class", []):
                print(color(f"Class {self.char_class} không thể trang bị {item}!", "red"))
                return
        self.equipment[it["type"]] = item
        print(color(f"Đã trang bị {item}!", "green"))
    def use_item(self, item):
        if item not in self.inventory:
            print(color("Bạn không có vật phẩm này!", "red"))
            return
        it = ITEM_DATABASE[item]
        if it["type"] == "thuốc":
            if "HP" in it:
                self.hp = min(self.max_hp, self.hp + it["HP"])
                print(color(f"Hồi {it['HP']} HP!", "green"))
            if "MP" in it:
                self.mp = min(self.max_mp, self.mp + it["MP"])
                print(color(f"Hồi {it['MP']} MP!", "blue"))
            self.inventory.remove(item)
        else:
            self.equip(item)
    def gain_exp(self, amount):
        self.exp += amount
        up = False
        while self.exp >= 30 + self.level * 10:
            self.exp -= 30 + self.level * 10
            self.level += 1
            self.skill_points += 1
            self.max_hp += 5
            self.max_mp += 2
            print(color(f"🌟 LÊN CẤP! {self.level}", "yellow"))
            up = True
        if up:
            self.hp = self.max_hp
            self.mp = self.max_mp
        if self.level >= 30 and self.sub_class is None:
         print("Bạn đã đủ điều kiện chọn nghề phụ (multi-class)!")
         choose_subclass(self)

def rebirth(hero):
    print("Bạn đã chuyển sinh! Bắt đầu lại với một phần sức mạnh cũ.")
    keep_skills = []
    if hero.unlocked_skills:
        print("Các kỹ năng bạn đã học: ", hero.unlocked_skills)
        n = min(2, len(hero.unlocked_skills))  # Cho giữ lại tối đa 2 kỹ năng
        for i in range(n):
            print(f"Chọn kỹ năng giữ lại số {i+1}:")
            for j, sk in enumerate(hero.unlocked_skills,1):
                print(f"{j}. {sk}")
            idx = input("Nhập số kỹ năng muốn giữ: ")
            if idx.isdigit() and 1 <= int(idx) <= len(hero.unlocked_skills):
                keep_skills.append(hero.unlocked_skills[int(idx)-1])
                hero.unlocked_skills.pop(int(idx)-1)
    name = hero.name
    baseclass = hero.char_class
    # Tạo lại hero (có thể cho chọn lại nghề chính nếu muốn)
    new_hero = Hero(name, baseclass)
    new_hero.unlocked_skills = keep_skills
    new_hero.skills = keep_skills[:]
    new_hero.skill_points = 0
    print("Chuyển sinh thành công! Bạn giữ lại kỹ năng hiếm:", keep_skills)
    return new_hero

def upgrade_skill(hero):
    skills = SKILL_TREE.get(hero.char_class, {})
    available = [s for s, v in skills.items() if hero.level >= v["level"] and s not in hero.unlocked_skills]
    if not available:
        print("Không có kỹ năng mới để học.")
        return
    print("Kỹ năng có thể học:")
    for i, s in enumerate(available, 1):
        print(f"{i}. {s} ({skills[s]['desc']})")
    idx = input("Chọn kỹ năng số: ")
    if idx.isdigit() and 1 <= int(idx) <= len(available):
        skill = available[int(idx)-1]
        hero.unlocked_skills.append(skill)
        hero.skill_points -= 1
        hero.skills.append(skill)  # Nếu bạn muốn dùng kỹ năng này trong combat
        print(f"Đã học kỹ năng {skill}.")
    else:
        print("Chọn sai!")

def choose_class(hero, ach):
    print(color("Chọn class chuyển chức:", "cyan"))
    class_list = []
    for k, v in ADVANCED_CLASSES.items():
        if v.get("hidden") and not hero.job_secret:
            continue
        # Nếu hero là Vô nghề, cho phép chọn tất cả nghề thường (không ẩn)
        if hero.base_class == "Vô nghề" and not v.get("hidden"):
            class_list.append(k)
        elif v["base"] == hero.base_class:
            class_list.append(k)
    if not class_list:
        print(color("Không có class nào để chuyển!", "red"))
        return
    for i, c in enumerate(class_list):
        print(f"{i + 1}. {c}")
    while True:
        idx = input("Nhập số: ")
        if idx.isdigit() and 1 <= int(idx) <= len(class_list):
            cl = class_list[int(idx) - 1]
            print(color(f"Bạn quyết định trở thành {cl}!", "yellow"))
            stats = ADVANCED_CLASSES[cl]
            hero.char_class = cl
            hero.stats = dict(stats)
            hero.max_hp = stats["HP"]
            hero.hp = hero.max_hp
            hero.max_mp = stats["MP"]
            hero.mp = hero.max_mp
            hero.skills = CLASS_SKILLS[cl][:]
            hero.job_changed = True
            if stats.get("hidden"):
                ach.add("secret_class")
            return
        print(color("Chọn lại!", "red"))

def jobchange_event(hero, ach):
    rich_panel("Nghi lễ chuyển chức bắt đầu!\nBạn bước vào vòng sáng kỳ lạ... Đột nhiên, một bóng đen xuất hiện, thử thách bạn bằng chính bản thân bóng tối của mình!", "Chuyển Chức", "magenta")
    time.sleep(1.2)
    print(color("Bạn phải chiến đấu với \"Bản Ngã Bóng Tối\"!", "red"))
    enemy_hp = 40 + hero.level * 2
    hero_hp = hero.hp
    turn = 0
    while hero_hp > 0 and enemy_hp > 0:
        print(color(f"Bạn: {hero_hp}  | Bản ngã bóng tối: {enemy_hp}", "yellow"))
        print("1. Tấn công  2. Chịu đựng  3. Khích lệ bản thân")
        act = input("Chọn: ")
        if act == "1":
            dmg = 8 + random.randint(0, 3)
            print(color(f"Bạn tấn công gây {dmg} sát thương!", "red"))
            enemy_hp -= dmg
        elif act == "2":
            print(color("Bạn phòng thủ, giảm sát thương lượt này!", "cyan"))
        elif act == "3":
            print(color("Bạn tự khích lệ, hồi phục 9 HP!", "green"))
            hero_hp = min(hero.max_hp, hero_hp + 9)
        else:
            print(color("Bạn bối rối, trượt lượt!", "red"))
        if enemy_hp > 0:
            dmg = random.randint(6, 12)
            if act == "2": dmg //= 2
            hero_hp -= dmg
            print(color(f"Bản ngã bóng tối tấn công bạn gây {dmg} sát thương!", "red"))
        turn += 1
        time.sleep(0.5)
    if hero_hp > 0:
        print(color("Bạn đã vượt qua thử thách! Năng lượng mới tràn ngập trong bạn...", "green"))
        hidden_class = False
        if hero.treasure_count >= 5 and hero.pets and "Mảnh phép bí ẩn" in hero.inventory:
            print(color("Bí ẩn bóng tối trỗi dậy trong bạn... Bạn đã mở khóa class ẩn!", "magenta"))
            hero.job_secret = True
            hidden_class = True
        choose_class(hero, ach)
    else:
        print(color("Bạn thất bại... nhưng hành trình vẫn tiếp tục. Hãy luyện tập và thử lại khi mạnh hơn!", "red"))
        hero.hp = 1

class Pet:
    def __init__(self, name):
        self.name = name
        info = PET_DATABASE[name]
        self.hp = info["hp"]
        self.max_hp = info["hp"]
        self.atk = info["atk"]
        self.skill = info["skill"]
    def use_skill(self):
        print(color(f"{self.name} dùng kỹ năng: {self.skill}!", "cyan"))
        wait_enter()

class QuestSystem:
    def __init__(self):
        self.quests = [dict(q) for q in QUEST_DATABASE]
        self.progress = {}
        self.craft = []
    def on_kill(self, mob, place):
        for q in self.quests:
            if q["completed"]: continue
            req = q["requirements"]
            if "kill" in req and mob in req["kill"]:
                if req.get("place") and req["place"] != place:
                    continue
                self.progress[mob] = self.progress.get(mob, 0) + 1
                if self.progress[mob] >= req["kill"][mob]:
                    q["completed"] = True
                    rich_panel(f"✅ Hoàn thành nhiệm vụ: {q['name']}!", "Nhiệm vụ", "yellow")
    def on_event(self, event, place):
        for q in self.quests:
            if q["completed"]: continue
            req = q["requirements"]
            if req.get("event") == event and req.get("place") == place:
                q["completed"] = True
                rich_panel(f"✅ Hoàn thành nhiệm vụ: {q['name']}!", "Nhiệm vụ", "yellow")
    def on_craft(self, item):
        for q in self.quests:
            if q["completed"]: continue
            req = q["requirements"]
            if req.get("craft") == item:
                q["completed"] = True
                rich_panel(f"✅ Hoàn thành nhiệm vụ: {q['name']}!", "Nhiệm vụ", "yellow")
    def show(self):
        show_quest_progress(self.quests)
    def __init__(self):
        super().__init__()
        self.daily_quests = []
        self.last_daily = None

    def gen_daily_quests(self):
        # Tạo nhiệm vụ ngày mới mỗi ngày
        today = datetime.date.today()
        if self.last_daily != today:
            self.daily_quests = [
                {"id": 100+random.randint(1,999), "name": "Nhiệm vụ ngày: Đánh bại 3 quái", "desc": "Đánh bại 3 quái bất kỳ.", "requirements": {"kill_any": 3}, "reward_exp": 25, "reward_gold": 15, "completed": False}
            ]
            self.last_daily = today

    def on_kill(self, mob, place):
        super().on_kill(mob, place)
        # Xử lý nhiệm vụ ngày
        self.gen_daily_quests()
        for q in self.daily_quests:
            if q["completed"]: continue
            if "kill_any" in q["requirements"]:
                q.setdefault("progress", 0)
                q["progress"] += 1
                if q["progress"] >= q["requirements"]["kill_any"]:
                    q["completed"] = True
                    rich_panel(f"✅ Hoàn thành nhiệm vụ ngày: {q['name']}!", "Nhiệm vụ ngày", "yellow")

    def show(self):
        super().show()
        self.gen_daily_quests()
        if self.daily_quests:
            print("=== NHIỆM VỤ NGÀY ===")
            for q in self.daily_quests:
                st = "[X]" if q["completed"] else "[ ]"
                print(f"{st} {q['name']}: {q['desc']}")

# Hệ thống nhiệm vụ ngẫu nhiên từ NPC
def random_side_quest():
    quests = [
        {"name": "Thu thập thảo dược", "desc": "Nhặt 2 vật phẩm bất kỳ ở đồng cỏ.", "requirements": {"gather": 2}, "reward_exp": 15, "reward_gold": 10, "completed": False},
        {"name": "Giao hàng", "desc": "Mang 1 món đồ đến Thành phố.", "requirements": {"deliver": 1}, "reward_exp": 20, "reward_gold": 12, "completed": False},
    ]
    return random.choice(quests)

def shop(hero):
    print(color("Cửa hàng:", "cyan"))
    items = list(ITEM_DATABASE.keys())
    for i, k in enumerate(items):
        price = 15 + i*7
        qual = ITEM_DATABASE[k].get("quality", "thường")
        print(f"{i+1}. {k} - {ITEM_DATABASE[k]['desc']} [{qual}] (Giá: {price})")
    print("0. Thoát")
    idx = input("Mua vật phẩm số? ")
    if idx == "0": return
    if idx.isdigit() and 1 <= int(idx) <= len(items):
        item = items[int(idx)-1]
        price = 15 + (int(idx)-1)*7
        if hero.gold < price:
            print(color("Không đủ vàng!", "red"))
            return
        hero.gold -= price
        hero.inventory.append(item)
        print(color(f"Đã mua {item}!", "green"))
    else:
        print(color("Chọn lại!", "red"))

def random_event(hero, pet, quests, ach, daynight):
    curr = MAP_LAYOUT[hero.map_x][hero.map_y]
    hero.steps += 1
    zone_danger = curr in ["Hang động", "Khu rừng cổ", "Núi tuyết", "Lâu đài"]
    night = (daynight=="Đêm")
    event_prob = 40 if night or zone_danger else 22
    if hero.level >= 20 and not hero.job_unlocked and hero.char_class == "Vô nghề":
        if curr == "Làng":
            event = {"name": "nghi_le_chuyen_sinh", "desc": "Nghi lễ chuyển chức bắt đầu! Một thử thách sinh tử đang chờ bạn...", "reward": "jobchange"}
        else:
            event = random.choices(EVENTS, weights=[2,2,1,1,2,2])[0]
    elif random.randint(1, 100) > event_prob:
        return
    else:
        event = random.choices(EVENTS, weights=[3,3,2,2,2,2])[0]
    rich_panel(event["desc"], "Sự kiện", "magenta")
    if event["reward"] == "random_item":
        item = random.choice(list(ITEM_DATABASE.keys()))
        hero.inventory.append(item)
        print(color(f"Bạn nhặt được: {item}", "yellow"))
        hero.treasure_count += 1
        if hero.treasure_count >= 5:
            ach.add("treasure_hunter")
        quests.on_event("kho_bau", curr)
    elif event["reward"] == "full_heal":
        hero.hp = hero.max_hp
        hero.mp = hero.max_mp
        print(color("HP/MP đã hồi đầy!", "green"))
    elif event["reward"] == "shop":
        shop(hero)
    elif event["reward"] == "mini_game":
        mini_game(hero)
        quests.on_event("mini_game", curr)
    elif event["reward"] == "trap":
        if hero.steps <= 5 or hero.level == 1:
            print(color("Bạn suýt dính bẫy, nhưng đã kịp tránh nhờ linh cảm!", "cyan"))
        else:
            dmg = random.randint(3, 7)
            hero.hp = max(1, hero.hp - dmg)
            print(color(f"Bạn mất {dmg} HP do bẫy!", "red"))
    elif event["reward"] == "npc_an":
        if random.randint(0,1):
            hero.gold += 10
            print(color("NPC tặng bạn 10 vàng!", "yellow"))
        else:
            item = "Thuốc máu"
            hero.inventory.append(item)
            print(color("NPC cho bạn 1 Thuốc máu!", "green"))
    elif event["reward"] == "jobchange":
        hero.job_unlocked = True
        jobchange_event(hero, ach)
    if hero.hp < hero.max_hp:
        hero.hp += 2
        print(color("Bạn hồi phục 2 HP nhờ nghỉ ngơi trên đường đi.", "cyan"))
    wait_enter()

def mini_game(hero):
    print(color("Mini-game: Đoán số (1-10)", "magenta"))
    answer = random.randint(1, 10)
    for i in range(3):
        guess = input(f"Lần {i+1}: ")
        if guess.isdigit() and int(guess) == answer:
            print(color("Chính xác! Bạn nhận 10 vàng.", "green"))
            hero.gold += 10
            return True
        elif guess.isdigit() and int(guess) < answer:
            print("Số lớn hơn!")
        else:
            print("Số nhỏ hơn!")
    print(color(f"Bạn thua! Số đúng là {answer}", "red"))
    return False

def battle(hero, pet, quests, ach, daynight):
    curr = MAP_LAYOUT[hero.map_x][hero.map_y]
    area = curr

    # Lọc danh sách quái vật theo vùng
    candidates = AREA_MONSTERS.get(area, ["Slime"])
    # Lọc thêm theo level nếu muốn
    minlv, maxlv = AREA_LEVEL_HINT.get(area, (1, 99))
    suitable = []
    for m in candidates:
        # Nếu là boss thì chỉ cho gặp khi level đủ lớn
        if m in ["Dark Lord", "Quỷ vương", "Pháp sư cổ đại", "Rồng Lửa", "Hổ Băng"] and hero.level < minlv:
            continue
        suitable.append(m)
    if not suitable:
        suitable = ["Slime"]
    mobname = random.choice(suitable)
    mob = dict(MONSTER_DATABASE[mobname])
    print(color(f"Gặp {mobname}!", "red"))
    show_ascii(mobname)
    mhp = mob["HP"] + (hero.level//5)*6
    while mhp > 0 and hero.hp > 0:
        print(color(f"Bạn: {hero.hp}/{hero.max_hp} | {mobname}: {mhp}", "yellow"))
        if pet:
            print(color(f"{pet.name} tấn công {mobname} gây {pet.atk} sát thương!", "green"))
            mhp -= pet.atk
        act = input("1. Tấn công  2. Kỹ năng  3. Pet skill  4. Dùng item  5. Chạy: ")
        if act == "1":
            dmg = hero.stats["STR"] + random.randint(0, 2)
            if hero.equipment.get("vũ khí"):
                it = ITEM_DATABASE[hero.equipment["vũ khí"]]
                dmg += it.get("STR",0) + it.get("DEX",0) + it.get("INT",0)
            print(color(f"Bạn tấn công {mobname} gây {dmg} sát thương!", "yellow"))
            mhp -= dmg
        elif act == "2":
            if not hero.skills:
                print(color("Bạn chưa có kỹ năng!", "red"))
                continue
            print("Kỹ năng:")
            for i, s in enumerate(hero.skills):
                print(f"{i+1}. {s}")
            sidx = input("Chọn kỹ năng: ")
            if sidx.isdigit() and 1 <= int(sidx) <= len(hero.skills):
                skill = hero.skills[int(sidx)-1]
                if skill in ["Chém nhanh","Chém xoáy","Thánh kiếm"]:
                    dmg = hero.stats["STR"]*2 + hero.level
                    print(color(f"Bạn dùng {skill} gây {dmg} sát thương!", "red"))
                    mhp -= dmg
                elif skill in ["Quả cầu lửa","Lốc xoáy lửa","Thiên hỏa"]:
                    dmg = hero.stats["INT"]*2 + hero.level*2
                    print(color(f"Bạn dùng {skill} gây {dmg} sát thương phép!", "blue"))
                    mhp -= dmg
                elif skill in ["Hồi phục","Hồi sinh"]:
                    heal = 12 + hero.stats["INT"]
                    hero.hp = min(hero.max_hp, hero.hp + heal)
                    print(color(f"Bạn hồi phục {heal} HP!", "green"))
                elif skill in ["Phòng ngự","Khiên phép","Kháng phép","Bất khả chiến bại","Hộ thể","Bất khuất"]:
                    print(color("Bạn tăng phòng thủ lượt này!", "cyan"))
                elif skill in ["Đâm lén","Cú đâm chí mạng","Đoạt mệnh"]:
                    dmg = hero.stats["STR"] + hero.stats["DEX"] + hero.level
                    print(color(f"Bạn dùng {skill} gây {dmg} sát thương!", "magenta"))
                    mhp -= dmg
                elif skill in ["Tàng hình","Ẩn thân","Ẩn thân vô hình"]:
                    print(color("Bạn tránh đòn lượt này!", "cyan"))
                elif skill in ["Mũi tên thần","Bão tên","Bắn 3 mũi"]:
                    dmg = hero.stats["DEX"]*2 + hero.level
                    print(color(f"Bạn dùng {skill} gây {dmg} sát thương tầm xa!", "yellow"))
                    mhp -= dmg
                elif skill in ["Bẫy độc","Bẫy dây"]:
                    print(color("Bạn đặt bẫy, lượt sau quái vật nhận thêm sát thương!", "green"))
                elif skill in ["Liên hoàn cước","Cú đấm sấm sét","Tuyệt kỹ quyền vương"]:
                    dmg = hero.stats["STR"]*2 + hero.stats["DEX"] + hero.level
                    print(color(f"Bạn tung {skill} gây {dmg} sát thương!", "red"))
                    mhp -= dmg
                elif skill in ["Khích lệ"]:
                    hero.hp = min(hero.max_hp, hero.hp + 10)
                    print(color("Bạn hồi phục 10 HP!", "green"))
                elif skill in ["Ảo ảnh"]:
                    print(color("Tạo ra ảo ảnh, giảm sát thương nhận vào!", "cyan"))
                elif skill in ["Kiếm khí"]:
                    dmg = hero.stats["STR"] + hero.stats["DEX"] + 3
                    print(color(f"Bạn dùng {skill} gây {dmg} sát thương!", "yellow"))
                    mhp -= dmg
                elif skill in ["Cường hóa"]:
                    hero.stats["STR"] += 2
                    print(color("Sức mạnh tạm thời tăng lên!", "magenta"))
        elif act == "3" and pet:
            pet.use_skill()
            mhp -= pet.atk + 2
        elif act == "4":
            print("Túi đồ:", hero.inventory)
            item = input("Dùng/trang bị vật phẩm gì (nhập tên, Enter để bỏ qua): ")
            if item:
                hero.use_item(item)
        elif act == "5":
            print(color("Bạn đã chạy thoát!", "cyan"))
            return
        if mhp > 0:
            mobdmg = mob["STR"] + random.randint(0, 2) + (hero.level//7)
            hero.hp -= mobdmg
            print(color(f"{mobname} tấn công bạn gây {mobdmg} sát thương!", "red"))
    if hero.hp <= 0:
        if hero.char_class in ["Kiếm thánh","Pháp thần","Bóng ma","Thợ săn huyền thoại","Quyền vương"]:
            show_cutscene("ending_secret")
        else:
            show_cutscene("ending_bad")
        print(color("Bạn thua cuộc!", "red"))
        sys.exit()
    else:
        print(color(f"Bạn hạ {mobname}! Nhận {mob['EXP']} EXP, {mob['Gold']} vàng.", "green"))
        hero.gain_exp(mob["EXP"])
        hero.gold += mob["Gold"]
        drop = random.choice(mob["drops"])
        print(color(f"Nhặt được: {drop}", "yellow"))
        hero.inventory.append(drop)
        quests.on_kill(mobname, curr)
        if mobname == "Dark Lord":
            ach.add("boss_final")
            if hero.char_class in ["Kiếm thánh","Pháp thần","Bóng ma","Thợ săn huyền thoại","Quyền vương"]:
                show_cutscene("ending_secret")
            else:
                show_cutscene("ending_good")
            print(color("Bạn đã phá đảo game! Thành tựu: Đánh bại boss cuối!", "magenta"))
            show_achievements(ach)
            sys.exit()
        if mobname == "Yeti":
            hero.pets.append("Yeti")
        if len(set(hero.pets)) >= 3:
            ach.add("all_pets")

def pet_menu(hero, pet, ach):
    print(color(f"Pet hiện tại: {pet.name if pet else 'Không'}", "green"))
    print("1. Bắt pet mới  2. Gọi pet  0. Thoát")
    c = input("Chọn: ")
    if c == "1":
        avail = [k for k in PET_DATABASE if k not in hero.pets]
        if not avail:
            print(color("Bạn đã sở hữu tất cả pet!", "yellow"))
            return pet
        p = random.choice(avail)
        print(color(f"Bạn bắt được {p}!", "cyan"))
        hero.pets.append(p)
        if len(set(hero.pets)) >= 3:
            ach.add("all_pets")
        return Pet(p)
    elif c == "2":
        if pet:
            print(color(f"{pet.name} xuất trận!", "green"))
        else:
            print(color("Bạn chưa có pet!", "red"))
    return pet

def craft(hero, quests, ach):
    print(color("Chế tạo/cường hóa:", "cyan"))
    print("Vật phẩm chế tạo: 1. Vũ khí truyền thuyết (cần Mảnh phép bí ẩn+Kiếm sắt)")
    if "Mảnh phép bí ẩn" in hero.inventory and "Kiếm sắt" in hero.inventory:
        c = input("Chế tạo vũ khí truyền thuyết? (y/n): ")
        if c.lower()=="y":
            hero.inventory.remove("Mảnh phép bí ẩn")
            hero.inventory.remove("Kiếm sắt")
            hero.inventory.append("Kiếm truyền thuyết")
            print(color("Chế tạo thành công Kiếm truyền thuyết! (+6 STR, cực mạnh)", "magenta"))
            quests.on_craft("Mảnh phép bí ẩn")
            hero.craft_count += 1
    else:
        print(color("Bạn chưa đủ nguyên liệu!", "red"))
    if hero.craft_count >= 1:
        ach.add("secret_craft")

def save_game(hero, pet, quests, ach):
    try:
        with open("savegame.dat", "wb") as f:
            pickle.dump((hero, pet, quests, ach), f)
        print(color("Đã lưu game.", "green"))
    except:
        print(color("Không lưu được!", "red"))

def load_game():
    try:
        with open("savegame.dat", "rb") as f:
            hero, pet, quests, ach = pickle.load(f)
        return hero, pet, quests, ach
    except:
        print(color("Không có file lưu.", "red"))
        return None, None, None, set()

def get_daynight():
    h = datetime.datetime.now().hour
    return "Đêm" if h >= 18 or h < 6 else "Ngày"

# ==== MAIN ==== #
def main():
    big_title("HÀNH TRÌNH ANH HÙNG")
    show_cutscene("intro")
    hero, pet, quests, ach = None, None, None, set()
    while True:
        choice = main_menu()
        if choice == "new":
            name = input("Đặt tên cho nhân vật: ")
            hero = Hero(name, "Vô nghề")
            pet = None
            quests = QuestSystem()
            ach = set()
            break
        elif choice == "continue":
            hero, pet, quests, ach = load_game()
            if hero: break
        elif choice == "lore":
            show_lore()
        elif choice == "twist":
            show_twist()
        elif choice == "help":
            show_help()
        elif choice == "credit":
            show_credits()
        elif choice == "exit":
            print(color("Tạm biệt!", "magenta"))
            sys.exit()
    while True:
        clear_screen()
        daynight = get_daynight()
        hero.show(pet, daynight)
        print(color("\n1. Di chuyển  2. Đánh quái  3. Pet  4. Túi đồ  5. Nhiệm vụ  6. Cửa hàng  7. Chế tạo  8. Thành tựu  9. Lưu game  10. Nâng kỹ năng  0. Thoát", "yellow"))
        # Điều kiện chuyển nghề khi đủ level và chưa chuyển
        if hero.char_class == "Vô nghề" and (hero.level >= 20 or (hero.treasure_count >= 5 and hero.pets and "Mảnh phép bí ẩn" in hero.inventory)):
            print(color("!! Bạn đã đủ điều kiện chuyển nghề! Hãy đi đến Làng để kích hoạt nghi lễ chuyển sinh và chọn class.", "magenta"))
        act = input("Chọn hành động: ")
        if act == "1":
            print("W: lên  S: xuống  A: trái  D: phải")
            move = input("Đi: ").strip().upper()
            x, y = hero.map_x, hero.map_y
            if move == "W" and x > 0: hero.map_x -= 1
            elif move == "S" and x < len(MAP_LAYOUT) - 1: hero.map_x += 1
            elif move == "A" and y > 0: hero.map_y -= 1
            elif move == "D" and y < len(MAP_LAYOUT[0]) - 1: hero.map_y += 1
            else:
                print(color("Không thể đi!", "red"))
                wait_enter()
                continue
            transition_effect(MAP_LAYOUT[hero.map_x][hero.map_y])
            # Nếu đến Làng và đủ điều kiện chuyển nghề
            curr_loc = MAP_LAYOUT[hero.map_x][hero.map_y]
            if hero.char_class == "Vô nghề" and (hero.level >= 20 or (hero.treasure_count >= 5 and hero.pets and "Mảnh phép bí ẩn" in hero.inventory)) and curr_loc == "Làng" and not hero.job_unlocked:
                hero.job_unlocked = True
                jobchange_event(hero, ach)
            else:
                random_event(hero, pet, quests, ach, daynight)
        elif act == "2":
            battle(hero, pet, quests, ach, daynight)
            wait_enter()
        elif act == "3":
            pet = pet_menu(hero, pet, ach)
            wait_enter()
        elif act == "4":
            print("Túi đồ:", hero.inventory)
            item = input("Dùng/trang bị vật phẩm gì (nhập tên, Enter để bỏ qua): ")
            if item:
                hero.use_item(item)
            wait_enter()
        elif act == "5":
            quests.show()
            wait_enter()
        elif act == "6":
            shop(hero)
            wait_enter()
        elif act == "7":
            craft(hero, quests, ach)
            wait_enter()
        elif act == "8":
            show_achievements(ach)
        elif act == "9":
            save_game(hero, pet, quests, ach)
            wait_enter()
        elif act == "10":
         if hero.skill_points > 0:
            upgrade_skill(hero)
         else:
          print("Bạn không còn điểm kỹ năng.")
         wait_enter()
        elif act == "0":
            print(color("Tạm biệt! Lưu lại hành trình nhé!", "magenta"))
            sys.exit()
        else:
            print(color("Chọn lại!", "red"))

if __name__ == "__main__":
    main()
