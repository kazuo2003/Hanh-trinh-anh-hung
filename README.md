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
    ["Bờ biển",   "Khu rừng cổ", "Lâu đài"]
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
    "Lâu đài": "Nơi cuối cùng, boss mạnh nhất cư ngụ. Chỉ mở khi đủ điều kiện."
}
BASE_CLASSES = {
    "Nhà phiêu lưu": {"STR": 4, "DEX": 4, "VIT": 4, "INT": 4, "LUCK": 4, "HP": 28, "MP": 12}
}
ADVANCED_CLASSES = {
    # Lộ ra sau chuyển chức
    "Chiến binh": {"STR": 8, "DEX": 3, "VIT": 8, "INT": 1, "LUCK": 2, "HP": 38, "MP": 12},
    "Pháp sư":    {"STR": 2, "DEX": 4, "VIT": 4, "INT": 11, "LUCK": 3, "HP": 25, "MP": 32},
    "Sát thủ":    {"STR": 6, "DEX": 8, "VIT": 4, "INT": 2, "LUCK": 5, "HP": 29, "MP": 11},
    # Class ẩn (ẩn khi chưa đủ điều kiện)
    "Anh hùng bóng tối": {"STR": 10, "DEX": 6, "VIT": 7, "INT": 8, "LUCK": 7, "HP": 42, "MP": 18, "hidden": True}
}
CLASS_SKILLS = {
    "Chiến binh": ["Đòn Mạnh", "Khiên chắn"],
    "Pháp sư": ["Quả cầu lửa", "Hồi phục"],
    "Sát thủ": ["Đâm lén", "Tàng hình"],
    "Anh hùng bóng tối": ["Bóng tối vĩnh cửu", "Hồi phục bóng tối"],
    "Nhà phiêu lưu": ["Khích lệ"]
}
ITEM_DATABASE = {
    "Kiếm sắt": {"type": "vũ khí", "STR": 2, "desc": "Tăng 2 sức mạnh", "quality": "thường"},
    "Kiếm phép": {"type": "vũ khí", "INT": 3, "desc": "Tăng 3 trí tuệ", "quality": "hiếm"},
    "Áo giáp nhẹ": {"type": "áo giáp", "VIT": 2, "desc": "Tăng 2 thể chất", "quality": "thường"},
    "Nhẫn may mắn": {"type": "nhẫn", "LUCK": 2, "desc": "Tăng 2 may mắn", "quality": "hiếm"},
    "Thuốc máu": {"type": "thuốc", "HP": 20, "desc": "Hồi phục 20 HP"},
    "Thuốc mana": {"type": "thuốc", "MP": 15, "desc": "Hồi phục 15 MP"},
    "Mảnh phép bí ẩn": {"type": "chế", "desc": "Dùng để chế tạo vật phẩm cực mạnh", "quality": "siêu hiếm"}
}
MONSTER_DATABASE = {
    "Slime": {"HP": 18, "MP": 0, "STR": 3, "DEX": 2, "VIT": 2, "EXP": 8, "Gold": 5, "drops": ["Thuốc máu"]},
    "Goblin": {"HP": 22, "MP": 2, "STR": 4, "DEX": 3, "VIT": 3, "EXP": 12, "Gold": 7, "drops": ["Kiếm sắt", "Thuốc máu"]},
    "Drake": {"HP": 36, "MP": 0, "STR": 7, "DEX": 5, "VIT": 5, "EXP": 25, "Gold": 15, "drops": ["Kiếm phép", "Nhẫn may mắn"]},
    "Yeti": {"HP": 45, "MP": 0, "STR": 8, "DEX": 3, "VIT": 8, "EXP": 35, "Gold": 21, "drops": ["Áo giáp nhẹ", "Thuốc máu"]},
    "Dark Lord": {"HP": 110, "MP": 35, "STR": 18, "DEX": 9, "VIT": 13, "EXP": 140, "Gold": 100, "drops": ["Mảnh phép bí ẩn"]}
}
PET_DATABASE = {
    "Slime": {"hp": 24, "atk": 4, "skill": "Múc dính"},
    "Drake": {"hp": 40, "atk": 8, "skill": "Lửa phun"},
    "Yeti": {"hp": 50, "atk": 12, "skill": "Gầm băng giá"}
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
    {"name": "Chuyển chức thành Anh hùng bóng tối", "desc": "Khám phá class ẩn và chuyển chức thành công.", "condition": "dark_hero"}
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
                cell = f"{marker} {loc}" if loc else ""
                cells.append(cell)
            table.add_row(*cells)
        console.print(Align.center(table))
    else:
        print(color("BẢN ĐỒ:", "cyan"))
        for i, row in enumerate(MAP_LAYOUT):
            for j, loc in enumerate(row):
                if not loc: continue
                marker = "[*]" if hero.map_x == i and hero.map_y == j else "   "
                print(f"{marker} {loc}", end="\t")
            print()
    loc = MAP_LAYOUT[hero.map_x][hero.map_y]
    print(color(f"Địa điểm: {loc} - {MAP_DESC[loc]}", "yellow"))

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

def main_menu():
    if RICH:
        options = [
            ("🌟 Bắt đầu game mới", "new"),
            ("💾 Tiếp tục game", "continue"),
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
        print("1. Bắt đầu game mới\n2. Tiếp tục game\n3. Credits\n4. Thoát")
    while True:
        c = input("Chọn số: ")
        if c in "1234":
            return ["new", "continue", "credit", "exit"][int(c)-1]
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
    def __init__(self, name):
        base = BASE_CLASSES["Nhà phiêu lưu"]
        self.name = name
        self.char_class = "Nhà phiêu lưu"
        self.level = 1
        self.exp = 0
        self.gold = 20
        self.stats = dict(base)
        self.max_hp = base["HP"]
        self.hp = self.max_hp
        self.max_mp = base["MP"]
        self.mp = self.max_mp
        self.inventory = ["Thuốc máu", "Thuốc máu", "Thuốc máu"]
        self.equipment = {"vũ khí": None, "áo giáp": None, "nhẫn": None}
        self.skills = CLASS_SKILLS["Nhà phiêu lưu"][:]
        self.map_x, self.map_y = 0, 0
        self.craft_count = 0
        self.treasure_count = 0
        self.pets = []
        self.steps = 0
        self.job_unlocked = False
        self.job_changed = False
        self.job_secret = False
    def show(self, pet=None, daynight="Ngày"):
        show_status(self, pet, daynight)
        show_ascii(self.char_class if self.char_class != "Nhà phiêu lưu" else "Hero", is_hero=True)
        show_map(self)
    def equip(self, item):
        it = ITEM_DATABASE[item]
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
        while self.exp >= 30 + self.level*10:
            self.exp -= 30 + self.level*10
            self.level += 1
            self.max_hp += 5
            self.max_mp += 2
            print(color(f"🌟 LÊN CẤP! {self.level}", "yellow"))
            up = True
        if up:
            self.hp = self.max_hp
            self.mp = self.max_mp

def choose_class(hero, ach):
    # Chỉ mở khi hero đạt level>=20 và chưa chuyển class
    print(color("Chọn class chuyển chức:", "cyan"))
    class_list = []
    for k,v in ADVANCED_CLASSES.items():
        if v.get("hidden") and not hero.job_secret:
            continue
        class_list.append(k)
    for i, c in enumerate(class_list):
        print(f"{i+1}. {c}")
    while True:
        idx = input("Nhập số: ")
        if idx.isdigit() and 1 <= int(idx) <= len(class_list):
            cl = class_list[int(idx)-1]
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
            if cl == "Anh hùng bóng tối":
                ach.add("dark_hero")
            return
        print(color("Chọn lại!", "red"))

def jobchange_event(hero, ach):
    rich_panel("Nghi lễ chuyển chức bắt đầu!\nBạn bước vào vòng sáng kỳ lạ... Đột nhiên, một bóng đen xuất hiện, thử thách bạn bằng chính bản thân bóng tối của mình!", "Nghi lễ chuyển sinh", "magenta")
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
            dmg = 8 + random.randint(0,3)
            print(color(f"Bạn tấn công gây {dmg} sát thương!", "red"))
            enemy_hp -= dmg
        elif act == "2":
            print(color("Bạn phòng thủ, giảm sát thương lượt này!", "cyan"))
        elif act == "3":
            print(color("Bạn tự khích lệ, hồi phục 9 HP!", "green"))
            hero_hp = min(hero.max_hp, hero_hp+9)
        else:
            print(color("Bạn bối rối, trượt lượt!", "red"))
        if enemy_hp > 0:
            dmg = random.randint(6,12)
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

    # Kịch tính hơn: ban đêm xác suất sự kiện nguy hiểm cao, vùng nguy hiểm thì cả ban ngày cũng tăng
    zone_danger = curr in ["Hang động", "Khu rừng cổ", "Núi tuyết", "Lâu đài"]
    night = (daynight=="Đêm")
    event_prob = 40 if night or zone_danger else 22
    if hero.level >= 20 and not hero.job_unlocked:
        # Đến cấp 20 tự động mở sự kiện chuyển chức ở làng
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
    if curr == "Lâu đài" and hero.level < 6:
        print(color("Bạn chưa đủ mạnh để vào Lâu đài!", "red"))
        return
    # Boss/mini-boss đặc biệt
    if curr == "Lâu đài":
        mobname = "Dark Lord"
    elif curr == "Khu rừng cổ" and random.randint(1, 100) < 50:
        mobname = "Drake"
    elif curr == "Núi tuyết" and random.randint(1, 100) < 40:
        mobname = "Yeti"
    else:
        mobname = random.choice(list(MONSTER_DATABASE.keys()))
    mob = dict(MONSTER_DATABASE[mobname])
    print(color(f"Gặp {mobname}!", "red"))
    show_ascii(mobname)
    mhp = mob["HP"] + (hero.level//5)*6  # tăng độ khó!
    while mhp > 0 and hero.hp > 0:
        print(color(f"Bạn: {hero.hp}/{hero.max_hp} | {mobname}: {mhp}", "yellow"))
        if pet:
            print(color(f"{pet.name} tấn công {mobname} gây {pet.atk} sát thương!", "green"))
            mhp -= pet.atk
        act = input("1. Tấn công  2. Kỹ năng  3. Pet skill  4. Dùng item  5. Chạy: ")
        if act == "1":
            dmg = hero.stats["STR"] + random.randint(0, 2)
            print(color(f"Bạn tấn công {mobname} gây {dmg} sát thương!", "yellow"))
            mhp -= dmg
        elif act == "2":
            print("Kỹ năng:")
            for i, s in enumerate(hero.skills):
                print(f"{i+1}. {s}")
            sidx = input("Chọn kỹ năng: ")
            if sidx.isdigit() and 1 <= int(sidx) <= len(hero.skills):
                skill = hero.skills[int(sidx)-1]
                if skill == "Đòn Mạnh":
                    dmg = hero.stats["STR"]*2 + hero.level
                    print(color(f"Bạn dùng {skill} gây {dmg} sát thương!", "red"))
                    mhp -= dmg
                elif skill == "Quả cầu lửa":
                    dmg = hero.stats["INT"]*2 + hero.level*2
                    print(color(f"Bạn dùng {skill} gây {dmg} sát thương phép!", "blue"))
                    mhp -= dmg
                elif skill == "Hồi phục":
                    heal = 12 + hero.stats["INT"]
                    hero.hp = min(hero.max_hp, hero.hp + heal)
                    print(color(f"Bạn hồi phục {heal} HP!", "green"))
                elif skill == "Khiên chắn":
                    print(color("Bạn tăng phòng thủ lượt này!", "cyan"))
                elif skill == "Đâm lén":
                    dmg = hero.stats["STR"] + hero.stats["DEX"] + hero.level
                    print(color(f"Bạn đâm lén gây {dmg} sát thương!", "magenta"))
                    mhp -= dmg
                elif skill == "Tàng hình":
                    print(color("Bạn tránh đòn lượt này!", "cyan"))
                elif skill == "Bóng tối vĩnh cửu":
                    dmg = hero.stats["STR"]+hero.stats["INT"]+8
                    print(color(f"Bạn giải phóng bóng tối gây {dmg} sát thương!", "red"))
                    mhp -= dmg
                elif skill == "Hồi phục bóng tối":
                    heal = 18 + hero.stats["INT"]
                    hero.hp = min(hero.max_hp, hero.hp + heal)
                    print(color(f"Bóng tối hồi phục {heal} HP cho bạn!", "magenta"))
                elif skill == "Khích lệ":
                    hero.hp = min(hero.max_hp, hero.hp + 10)
                    print(color("Bạn hồi phục 10 HP!", "green"))
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
        if hero.char_class == "Anh hùng bóng tối":
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
            if hero.char_class == "Anh hùng bóng tối":
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
            name = input("Đặt tên cho Nhà phiêu lưu của bạn: ")
            hero = Hero(name)
            pet = None
            quests = QuestSystem()
            ach = set()
            break
        elif choice == "continue":
            hero, pet, quests, ach = load_game()
            if hero: break
        elif choice == "credit":
            show_credits()
        elif choice == "exit":
            print(color("Tạm biệt!", "magenta"))
            sys.exit()
    while True:
        clear_screen()
        daynight = get_daynight()
        hero.show(pet, daynight)
        print(color("\n1. Di chuyển  2. Đánh quái  3. Pet  4. Túi đồ  5. Nhiệm vụ  6. Cửa hàng  7. Chế tạo  8. Thành tựu  9. Lưu game  0. Thoát", "yellow"))
        if hero.level >= 20 and hero.job_unlocked and not hero.job_changed:
            print(color("!! Bạn đã đủ điều kiện chuyển chức! Hãy đi đến Làng để kích hoạt nghi lễ chuyển sinh và chọn class.", "magenta"))
        act = input("Chọn hành động: ")
        if act == "1":
            print("W: lên  S: xuống  A: trái  D: phải")
            move = input("Đi: ").strip().upper()
            x,y = hero.map_x, hero.map_y
            if move == "W" and x > 0: hero.map_x -= 1
            elif move == "S" and x < len(MAP_LAYOUT)-1: hero.map_x += 1
            elif move == "A" and y > 0: hero.map_y -= 1
            elif move == "D" and y < len(MAP_LAYOUT[0])-1: hero.map_y += 1
            else:
                print(color("Không thể đi!", "red"))
                wait_enter()
                continue
            transition_effect(MAP_LAYOUT[hero.map_x][hero.map_y])
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
        elif act == "0":
            print(color("Tạm biệt! Lưu lại hành trình nhé!", "magenta"))
            sys.exit()
        else:
            print(color("Chọn lại!", "red"))

if __name__ == "__main__":
    main()
