from random import randint
from colorama import Fore, Back, Style

global size_board


#  Общий класс для всех исключений
class AllException(Exception):
    pass


class BoardOutException(AllException):
    def __str__(self):
        return Fore.RED + Style.BRIGHT + "⚡ Вы выстрелили в клетку за пределами поля. " \
                                         "Повторите выстрел" + Style.RESET_ALL


class PreviouslyShotCellException(AllException):
    def __str__(self):
        return Fore.RED + Style.BRIGHT + "⚡ Вы ранее стреляли в эту клетку на поле. Повторите выстрел" + Style.RESET_ALL


#  Исключение, когда рандомно не удается разместить все корабли на поле
class ShipOutBoardException(AllException):
    def __str__(self):
        print("Корабль размещен за пределами поля")
        pass


class Dot:
    #  Точки на поле
    #  Класс для обозначения точек в игре.
    def __init__(self, x, y):
        self.x = x
        self.y = y

    #  Проверка произведен ли выстрел в эту же точку или размещен корабль
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    #  Для отображения если точка в списке
    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, orientation=0):
        self.bow = bow  # Координаты носа корабля
        self.length = length  # Длина корабля
        self.orientation = orientation  # 0 - горизонтальное, 1 - вертикальное
        self.lives = length  # Жизнь корабля

    #   Список всех точек корабля
    @property  # превращаем метод dots в свойство класса Ship
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cord_x = self.bow.x
            cord_y = self.bow.y
            if self.orientation == 1:
                cord_x += i
            elif self.orientation == 0:
                cord_y += i

            ship_dots.append(Dot(cord_x, cord_y))

        return ship_dots

    # Проверка попадания выстрелом по кораблю т.е попали ли нет в корабль
    def hit(self, shot):
        return shot in self.dots


class Board:

    def __init__(self, hid=False, size=6):
        self.size = size  # Размер игровой доски по умолчанию 6х6
        self.hid = hid  # Скрывать игровую доску по умолчанию скрываем

        self.count_destroy_ships = 0  # Кол-во уничтоженных кораблей
        self.empty_cell = Fore.LIGHTBLUE_EX + Style.BRIGHT + "⛆" + Style.RESET_ALL  # Обозначение пустой ячейки
        self.field = [[self.empty_cell] * size for _ in range(size)]  # Создание поля
        self.columns = [["   |"] + [str(j + 1) + " " + "| " for j in range(size)]]  # Обозначение столбцов
        self.busy_dots = []  # Список занятых точек, кораблями и их ареалом и выстрелами
        self.ships = []  # Список кораблей доски

    def __str__(self):

        # Создаем игровое поле
        cell = " ".join((' '.join(map(str, col)) for col in self.columns))
        for i, row in enumerate(self.field):
            cell += f"\n{i + 1}  | " + " | ".join(row) + " |"

        # Скрывать корабли на доске
        if self.hid:
            cell = cell.replace("⛴", self.empty_cell)
        return cell

    #  Проверка выходит ли корабль или произведен ли выстрел за пределы игрового поля
    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    #  Ареал вокруг корабля, чтобы рядом нельзя ставить другие корабли
    def contour(self, ship, verb=False):
        # координаты вокруг корабля
        around = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        # Создаем ареал вокруг корабля
        for d in ship.dots:
            for dx, dy in around:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy_dots:
                    if verb:
                        #  Обозначение ареала уничтоженного корабля
                        self.field[cur.x][cur.y] = Fore.LIGHTBLACK_EX + Style.BRIGHT + "⛭" + Style.RESET_ALL
                    #  Запись ареала корабля
                    self.busy_dots.append(cur)

    #  Добавление корабля на доску
    def add_ship(self, ship):
        for d in ship.dots:
            #  Проверка вылезает ли часть корабля за пределы поля или стоит ли корабль рядом с другим
            if self.out(d) or d in self.busy_dots:
                raise ShipOutBoardException()
        for d in ship.dots:
            #  Обозначение корабля
            self.field[d.x][d.y] = Fore.LIGHTYELLOW_EX + Style.BRIGHT + "⛴" + Style.RESET_ALL
            #  Запись координат корабля
            self.busy_dots.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        # Если произведен выстрел за пределы поля
        if self.out(d):
            raise BoardOutException()
        # Если произведен выстрел по координате второй раз
        if d in self.busy_dots:
            raise PreviouslyShotCellException()
        # Запись координат выстрела
        self.busy_dots.append(d)
        # Проверка попадания выстрела в корабль
        for ship in self.ships:
            if ship.hit(d):
                # Если попали, уменьшаем кол-во жизни корабля
                ship.lives -= 1
                # Помечаем на поле подбитый корабль
                self.field[d.x][d.y] = Fore.RED + Style.BRIGHT + "☠" + Style.RESET_ALL
                # Проверка кол-во жизней корабля
                if ship.lives == 0:
                    # Если уничтожен корабль, то увеличиваем счет потопленных кораблей
                    self.count_destroy_ships += 1
                    # Помечаем на поле, что вокруг потопленного корабля не может быть других кораблей.
                    self.contour(ship, verb=True)
                    print(Fore.MAGENTA + Style.BRIGHT + "⚔ Корабль уничтожен!" + Style.RESET_ALL)
                    return False
                else:
                    print(Fore.GREEN + Style.BRIGHT + "⚔ Корабль повреждён!" + Style.RESET_ALL)
                    # Повторить ход
                    return True
        # Если выстрел произведен в пустую клетку, то помечаем и сообщаем
        self.field[d.x][d.y] = Fore.LIGHTBLACK_EX + Style.BRIGHT + "⛯" + Style.RESET_ALL
        print(Fore.BLUE + Style.BRIGHT + "Промах!" + Style.RESET_ALL)
        return False

    # Поскольку busy_dots используется как список координат для расстановки кораблей на поле до начала игры,
    # а после начала игры там будет список координат куда стрелял игрок.
    # Если не сбросить список перед началом игры, то стрелять игроку будет некуда так как будет все занято.
    # # Этот метод обнуляет список координат для расстановки кораблей перед началом игры.
    def pure_busy_dots(self):
        self.busy_dots = []

    #  Игра заканчивается если все корабли уничтожены у одной из сторон
    def defeat(self):
        return self.count_destroy_ships == len(self.ships)

    @property
    def full_board(self):
        list_coordinates = []
        for i in range(0, len(self.field)):
            for j in range(0, len(self.field[i])):
                list_coordinates.append(Dot(i, j))
        return len(list_coordinates) == len(self.busy_dots)


class Player:
    # Этот класс будет родителем для классов с AI и с пользователем
    def __init__(self, my_board, enemy_board):
        self.my_board = my_board
        self.enemy_board = enemy_board

    # метод, который «спрашивает» игрока, в какую клетку он делает выстрел.
    def ask(self):
        raise NotImplementedError()

    # Последствия хода игрока
    def move(self):
        while True:
            try:
                # "Спрашиваем" координаты выстрела
                target = self.ask()
                # Выстрел
                repeat = self.enemy_board.shot(target)
                # Если корабль "ранен", то повторить выстрел
                return repeat
            # Если выстрел за поле или по одно и той же координате, то заново стрелять
            except AllException as e:
                print(e)


class AI(Player):
    # Ходы компьютерного игрока
    def ask(self):
        d = Dot(randint(0, size_board - 1), randint(0, size_board - 1))
        print(Style.BRIGHT + f"Ход компьютера: {d.x + 1} {d.y + 1}" + Style.RESET_ALL)
        return d
    # Тут добавить логику выстрела


class User(Player):
    # Ходы реального игрока
    def ask(self):
        while True:
            # Ввод координат пользователя
            coordinates_shot = input(Fore.MAGENTA + Style.BRIGHT + "Ваш выстрел ⛶ : " + Style.RESET_ALL).split()
            # Проверка, что пользователем введены 2 координаты
            if len(coordinates_shot) != 2:
                print(Fore.RED + Style.BRIGHT + "⚡ Введите 2 координаты! " + Style.RESET_ALL)
                continue

            x, y = coordinates_shot
            # Проверка, что эти 2 числа, а не буквы или символы
            if not (x.isdigit()) or not (y.isdigit()):
                print(Fore.RED + Style.BRIGHT + "⚡ Введите числа! " + Style.RESET_ALL)
                continue

            x, y = int(x), int(y)
            # Возвращаем координаты выстрела с корректировкой (игровое поле начинается с 1, а индексы с 0)
            return Dot(x - 1, y - 1)


class SetupShips:
    def __init__(self, line_ship):
        self.line_ship = line_ship

    @property
    def setup_ship(self):
        while True:
            parameter_ship = input(
                Fore.MAGENTA + Style.BRIGHT + f'Введите координаты для {self.line_ship}'
                                              f'-палубного корабля: \nКоординаты носа - X Y '
                                              f'и расположение корабля: '
                                              f'0 - горизонтальное, 1 - вертикальное: ' + Style.RESET_ALL).split()

            if len(parameter_ship) != 3:
                print(Fore.RED + Style.BRIGHT + "⚡ Введите 3 цифры из которых 2 координаты носа корабля (X Y) "
                                                "и одна расположение корабля (0 или 1)! " + Style.RESET_ALL)
                continue

            x, y, r = parameter_ship
            # Проверка, что эти 3 числа, а не буквы или символы
            if not (x.isdigit() and y.isdigit() and r.isdigit()):
                print(Fore.RED + Style.BRIGHT + "⚡ Введите 3 числа! " + Style.RESET_ALL)
                continue

            if not (int(r) == 0 or int(r) == 1):
                print(Fore.RED + Style.BRIGHT + "⚡ Расположение корабля: "
                                                "0 - горизонтальное или 1 - вертикальное!" + Style.RESET_ALL)
                continue

            # (игровое поле начинается с 1, а индексы с 0)
            return Ship(Dot(int(x) - 1, int(y) - 1), length=self.line_ship, orientation=int(r))


class Game:
    def __init__(self):
        # Приветствие
        self.greet()
        # Размер доски
        self.size = self.survey
        # Создаем доску для пользователя
        pl = self.restart_board()  # Сделал чтобы игрок сам выбирал размещение кораблей
        # Создаем доску компьютерного игрока
        co = self.random_board()
        # Скрываем размещение кораблей на доске компьютера
        co.hid = True
        # Создаем компьютерного игрока
        self.ai = AI(co, pl)
        # Создаем пользовательского игрока
        self.us = User(pl, co)

        # Расставляем рандомно корабли на доске

    def user_board(self):
        # Список длины кораблей в зависимости от размера поля
        if self.size == 10:
            ships_lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        else:
            ships_lens = [3, 2, 2, 1, 1, 1, 1]  # Создаем возможность большего выбора размещения корабле
        # размер доски
        board = Board(size=self.size)
        # Попытки размещения всех кораблей на одной доске
        # attempts = 0
        for sl in ships_lens:
            while True:
                # Если некуда поставить корабль, то перезапускаем доску
                if board.full_board:
                    print(Fore.RED + Style.BRIGHT + '⚡ Некуда поставить корабль '
                                                    'доска будет перезапущена! ' + Style.RESET_ALL)
                    return None
                print(board)
                # Размещаем корабль
                ship = SetupShips(sl).setup_ship
                try:
                    # Получилось добавить корабль
                    board.add_ship(ship)
                    break
                # Не удалось добавить корабль
                except ShipOutBoardException:
                    print(Fore.RED + Style.BRIGHT + '⚡ Не удалось добавить корабль! '
                                                    'Введите другие параметры' + Style.RESET_ALL)
                    pass
        # Очистка координат размещенных кораблей, для того чтобы записывать координаты выстрелов
        board.pure_busy_dots()
        # Если удалось разместить все корабли, то создаем доску для начала игры
        return board

    # Расставляем рандомно корабли на доске
    def try_board(self):
        # Список длины кораблей в зависимости от размера поля
        if self.size == 10:
            ships_lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        else:
            ships_lens = [3, 2, 2, 1, 1, 1, 1]  # Создаем возможность большего выбора размещения корабле
        # размер доски
        board = Board(size=self.size)
        # Попытки размещения всех кораблей на одной доске
        attempts = 0
        for sl in ships_lens:
            while True:
                attempts += 1
                # Если кол-во попыток более 1000, то заново расставляем корабли
                if attempts > 1000:
                    return None
                # Размещаем корабль
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), sl, randint(0, 1))
                try:
                    # Получилось добавить корабль
                    board.add_ship(ship)
                    break
                # Не удалось добавить корабль
                except ShipOutBoardException:
                    pass
        # Очистка координат размещенных кораблей, для того чтобы записывать координаты выстрелов
        board.pure_busy_dots()
        # Если удалось разместить все корабли, то создаем доску для начала игры
        return board

    # Если не разместить корабли на доске, то этот метод перезапускает процедуру создания доски
    # с кораблями, пока не разместятся все корабли на доске.
    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def restart_board(self):
        board = None
        while board is None:
            board = self.user_add_ship
        return board

    # Приветствие пользователя
    @staticmethod
    def greet():
        print(Fore.CYAN + Style.BRIGHT + "------------------------")
        print("    Приветствуем вас    ")
        print("         в игре         ")
        print("       морской бой!     ")
        print("    ⛵      ☄     ⛵    ")
        print("------------------------")
        print("Предлагаем Вам 2 варианта игры:")
        print("1 - Доска 6Х6 и 7 кораблей 🔱")
        print("2 - Доска 10Х10 и 10 кораблей 🔱" + Style.RESET_ALL)
        # print(Fore.MAGENTA + Style.BRIGHT + "    формат ввода: x y   ")
        # print("    x - номер строки    ")
        # print("    y - номер столбца   " + Style.RESET_ALL)

    # Выводит на экран доски
    def print_boards(self):
        print(Fore.MAGENTA + Style.BRIGHT + "-" * 20)
        print("Доска пользователя:" + Style.RESET_ALL)
        print(self.us.my_board)
        print()
        print(Style.BRIGHT + "-" * 20)
        print("Доска компьютера:")
        print(self.ai.my_board)
        print("-" * 20 + Style.RESET_ALL)

    # Цикл ходов
    def loop(self):
        # номер хода
        num = 0
        while True:
            self.print_boards()
            # По четным ходам ходит пользователь по нечетным компьютер
            if num % 2 == 0:
                print(Fore.MAGENTA + Style.BRIGHT + "♘ Ходит пользователь!" + Style.RESET_ALL)
                print(Fore.MAGENTA + Style.BRIGHT + "Формат ввода: x y"
                                                    ", где x - номер строки; y - номер столбца " + Style.RESET_ALL)
                repeat = self.us.move()
            else:
                print(Style.BRIGHT + "♞ Ходит компьютер!" + Style.RESET_ALL)
                repeat = self.ai.move()
                # Если при текущем ходе поврежден корабль, то ходит еще раз этот же игрок.
            if repeat:
                num -= 1
            # Проверяется все ли корабли уничтожены у игрока
            if self.ai.my_board.defeat():
                self.print_boards()
                print("-" * 20)
                print("🏆" + Fore.GREEN + Style.BRIGHT + " Вы выиграли!" + Style.RESET_ALL)
                break

            if self.us.my_board.defeat():
                self.print_boards()
                print("-" * 20)
                print("🏆" + Back.WHITE + Fore.BLACK + Style.BRIGHT + " Компьютер выиграл!" + Style.RESET_ALL)
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

    @property
    def survey(self):
        global size_board
        while True:
            # Ввод типа игры
            type_game = input(Fore.MAGENTA + Style.BRIGHT + "Какой вариант игры "
                                                            "Вы выбираете 1 или 2 ? " + Style.RESET_ALL)
            # Проверка, что пользователем введено одно число
            if len(type_game) != 1:
                print(Fore.RED + Style.BRIGHT + "⚡ Введите одно число! " + Style.RESET_ALL)
                continue

            # Проверка, что это число
            if not (type_game.isdigit()):
                print(Fore.RED + Style.BRIGHT + "⚡ Введите число! " + Style.RESET_ALL)
                continue

            # Проверка, что это число 1 b
            if not (int(type_game) == 1 or 2):
                print(Fore.RED + Style.BRIGHT + "⚡ Введите либо 1 или 2 " + Style.RESET_ALL)
                continue

            # В зависимости от выбора типа игры выбираем размер игрового поля
            if int(type_game) == 1:
                self.size = 6
                size_board = self.size
            elif int(type_game) == 2:
                self.size = 10
                size_board = self.size
            else:
                print(Fore.RED + Style.BRIGHT + "⚡ Введите цифру 1 или 2: " + Style.RESET_ALL)
                continue
            return self.size

    @property
    def user_add_ship(self):
        while True:

            question_add_ship = input(
                Fore.MAGENTA + Style.BRIGHT + "Вы хотите расставить корабли рандомно или самостоятельно?"
                                              " (0 - рандомно, 1 - сами)? " + Style.RESET_ALL)
            if len(question_add_ship) != 1:
                print(Fore.RED + Style.BRIGHT + "⚡ Введите одно число! " + Style.RESET_ALL)
                continue

            # Проверка, что это число
            if not (question_add_ship.isdigit()):
                print(Fore.RED + Style.BRIGHT + "⚡ Введите число! " + Style.RESET_ALL)
                continue

            # Проверка, что это число 0 или 1
            if not (int(question_add_ship) == 0 or 1):
                print(Fore.RED + Style.BRIGHT + "⚡ Введите либо 0 или 1 " + Style.RESET_ALL)
                continue

            # В зависимости от выбора типа игры выбираем размер игрового поля
            if int(question_add_ship) == 0:
                user_field = self.random_board()
            elif int(question_add_ship) == 1:
                user_field = self.user_board()

            else:
                print(Fore.RED + Style.BRIGHT + "⚡ Введите цифру 0 или 1: " + Style.RESET_ALL)
                continue
            return user_field


g = Game()
g.start()
