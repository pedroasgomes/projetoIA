# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 120:
# 103468 Pedro Gomes
# 104156 Henrique Pimentel

import sys
import copy

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class BimaruState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = BimaruState.state_id
        BimaruState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

    # TODO ############################################## ILEGAL ##############################################
    def get_board(self):
        return self.board
    # TODO ############################################## ILEGAL ##############################################

class Board:
    """Representação interna de um tabuleiro de Bimaru."""

    def __init__(self):
        self.matrix = [['.' for _ in range(10)] for _ in range(10)]
        self.unexplored_hints = []
        self.bpieces_left_row = []
        self.bpieces_left_col = []
        self.empty_spaces_row = ['10' for _ in range(10)]
        self.empty_spaces_col = ['10' for _ in range(10)]
        self.boats = [4, 3, 2, 1]  # Where self.boats[size-1] = número de barcos que faltam por de tamanho 'size'

        self.unclosed_rows = list(range(10))
        self.unclosed_columns = list(range(10))

    def __str__(self):
        result = ""
        for row in self.matrix:
            for cell in row:
                if cell == 'w':
                    result += '.'
                else:
                    result += cell
            result += '\n'
        return result

    # ------------------------- Getters -------------------------

    def get_value(self, row: int, col: int):
        """Devolve o valor na respetiva posição do tabuleiro. Se estiver
        fora retorna None, se não houver peca retorna '_' """

        if self.is_inside_board(row, col):
            return str(self.matrix[row][col])
        else:
            return None

    def get_adjacent_vertical_values(self, row: int, col: int):
        """Devolve os valores imediatamente acima e abaixo,
        respetivamente. Devolve None se estiver fora do tabuleiro,
        devolve '.' se nao houver peca"""

        return self.get_value(row - 1, col), self.get_value(row + 1, col)

    def get_adjacent_horizontal_values(self, row: int, col: int):
        """Devolve os valores imediatamente à esquerda e à direita,
        respetivamente. Devolve None se estiver fora do tabuleiro,
        devolve '.' se nao houver peca"""

        return self.get_value(row, col - 1), self.get_value(row, col + 1)

    def get_all_hints(self):
        return self.unexplored_hints

    def get_bpieces_left_row(self, row: int):
        return self.bpieces_left_row[row]

    def get_bpieces_left_col(self, col: int):
        return self.bpieces_left_col[col]

    def get_empty_spaces_row(self, row: int):
        return self.empty_spaces_row[row]

    def get_empty_spaces_col(self, col: int):
        return self.empty_spaces_col[col]

    def get_boats_left(self, size: int):
        return self.boats[size - 1]

    def get_available_sizes(self):

        available_sizes = []

        for size in range(1, 5):
            if self.get_boats_left(size) > 0:
                available_sizes.append(size)

        return available_sizes

    def get_unclosed_rows(self):
        return self.unclosed_rows

    def get_unclosed_columns(self):
        return self.unclosed_columns

    # ------------------------- Low level functions -------------------------

    def change_tile(self, row: int, col: int, piece: str):

        self.matrix[row][col] = piece

    def add_piece(self, row: int, col: int, piece: str):

        if self.is_boat_piece(piece):
            self.update_bpieces_left(row, col)
        self.change_tile(row, col, piece)
        self.update_empty_spaces(row, col)

    def add_hint(self, row: int, col: int, piece: str):

        if self.is_water_piece(piece):
            self.add_piece(row, col, piece)
        elif self.is_center_piece(piece):
            self.place_boat(row, col, 1, 0, 0)
        else:
            self.add_piece(row, col, piece)
            self.unexplored_hints.append((row, col, piece))

    def remove_hint(self, row: int, col: int, piece: str):
        self.unexplored_hints.remove((row, col, piece))

    def sort_hints(self):
        """ Coloca peças 'M' no fim da queue já que essas peças podem não ter
        orientação e podem aumentar a ramificação da procura desnecessariamente."""
        self.unexplored_hints = sorted(self.unexplored_hints, key=lambda x: (x[2] == 'M'))

    def is_hints_empty(self):
        return not self.unexplored_hints

    def update_boats_left(self, size: int):
        self.boats[size - 1] -= 1

    def update_bpieces_left(self, row: int, col: int):
        self.bpieces_left_row[row] = str(int(self.bpieces_left_row[row]) - 1)
        self.bpieces_left_col[col] = str(int(self.bpieces_left_col[col]) - 1)

    def update_empty_spaces(self, row: int, col: int):
        self.empty_spaces_row[row] = str(int(self.empty_spaces_row[row]) - 1)
        self.empty_spaces_col[col] = str(int(self.empty_spaces_col[col]) - 1)

    def add_closed_row(self, row: int):
        self.unclosed_rows.remove(row)

    def add_closed_column(self, column: int):
        self.unclosed_columns.remove(column)

    def is_u_single(self, row: int, col: int):
        return all(value in ('w', 'W', None) for value in self.get_adjacent_horizontal_values(row, col)) and \
            all(value in ('w', 'W', None) for value in self.get_adjacent_vertical_values(row, col))

    def is_m_oriented(self, row: int, col: int):
        """
        Vai verificar se existe uma possivel orientacao da middle piece
        que seja obrigatoria. Verifica obrigatoriedade se uma row/column tem
        espaco para duas pecas, mas a outra nao.
        :return: 0 se nao houver orientacao clara, 1 se a orientacao for
        vertical, 2 se a orientacao for horizontal
        """

        # O MESMO SE APLICA AQUI (VER EM BAXIO)
        if any(value in ('w', 'W', None) for value in self.get_adjacent_horizontal_values(row, col)):
            return 1
        elif any(value in ('w', 'W', None) for value in self.get_adjacent_vertical_values(row, col)):
            return 2
        # Caso bpieces_left_row <= 1 e bpieces_left_col <= 1, vai levar a um estado impossivel no result.
        # Podíamos tratar da condição adiando-a dizendo que m nao tem orientacao e tratavamos dela depois
        # Mas assim encontramos logo o erro e podemos matar este ramo da arvore neste momento. Adiar
        # um ramo da arvore errado é a coisa mais burra
        elif int(self.get_bpieces_left_row(row)) <= 1:
            return 1
        elif int(self.get_bpieces_left_col(col)) <= 1:
            return 2
        else:
            return 0

    # ------------------------- Static functions -------------------------

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) passado como argumento
        e retorna uma instância da classe Board."""

        board = Board()
        rows = sys.stdin.readline().split()
        columns = sys.stdin.readline().split()

        for i in range(10):
            board.bpieces_left_row.append(rows[i + 1])  # Guarda o número total de peças por colocar na row[i]
            board.bpieces_left_col.append(columns[i + 1])  # Guarda o número total de peças por colocar na col[i]

        number_hints = sys.stdin.readline().split()
        for j in range(int(number_hints[0])):
            hint = sys.stdin.readline().split()
            board.add_hint(int(hint[1]), int(hint[2]), hint[3])
        board.sort_hints()  # Vai meter hints com M no fim da queue

        board.logic_away()  # TODO OOOOOOOOOOOOOOOOOO 1337

        return board

    @staticmethod
    def is_inside_board(row: int, col: int):
        return (0 <= row <= 9) and (0 <= col <= 9)

    @staticmethod
    def is_hint_piece(piece: str):
        return piece.isupper()

    @staticmethod
    def is_new_piece(piece: str):
        return piece.islower()

    @staticmethod
    def is_empty(piece: str):
        return piece == '.'

    @staticmethod
    def is_water_piece(piece: str):
        return piece.upper() == 'W'

    @staticmethod
    def is_boat_piece(piece: str):
        return piece.upper() in ['C', 'T', 'B', 'L', 'R', 'M', 'U']

    @staticmethod
    def is_center_piece(piece: str):
        return piece.upper() == 'C'

    @staticmethod
    def is_top_piece(piece: str):
        return piece.upper() == 'T'

    @staticmethod
    def is_bot_piece(piece: str):
        return piece.upper() == 'B'

    @staticmethod
    def is_left_piece(piece: str):
        return piece.upper() == 'L'

    @staticmethod
    def is_right_piece(piece: str):
        return piece.upper() == 'R'

    @staticmethod
    def is_middle_piece(piece: str):
        return piece.upper() == 'M'

    @staticmethod
    def is_unknown_piece(piece: str):
        return piece.upper() == 'U'

    # =========================== Upper level functions ===========================

    def flood_lines(self):

        for row in self.get_unclosed_rows():
            if self.get_bpieces_left_row(row) == '0':
                self.add_closed_row(row)
                for i in range(10):
                    if self.is_empty(self.get_value(row, i)):
                        self.add_piece(row, i, 'w')

        for col in self.get_unclosed_columns():
            if self.get_bpieces_left_col(col) == '0':
                self.add_closed_column(col)
                for i in range(10):
                    if self.is_empty(self.get_value(i, col)):
                        self.add_piece(i, col, 'w')

    def marshal_lines(self):

        boats = []
        boats_copy = self.boats.copy()

        for row in self.get_unclosed_rows():
            if self.get_bpieces_left_row(row) == self.get_empty_spaces_row(row): # Assume-se que nunca vai ser <= 0
                col = 0
                while col < 10:
                    size = 0
                    while (col + size < 10) and\
                            (self.is_empty(self.get_value(row, col)) or self.is_boat_piece(self.get_value(row, col))):
                        size += 1

                    if size == 1:
                        if self.is_u_single(row, col):
                            boats_copy[size - 1] -= 1
                            if boats_copy[size - 1] < 0:
                                return 1
                            boats.append((row, col, size, 0, 0))
                        else:
                            self.add_hint(row, col, 'U')
                        col += size

                    elif size < 5:  # Assume [2,3,4]
                        boats_copy[size - 1] -= 1
                        if boats_copy[size - 1] < 0:
                            return 1
                        boats.append((row, col, size, 0, 0))
                        col += size

                    elif size > 4:
                        return 1

                    else:
                        col += 1

        for col in self.get_unclosed_columns():
            if self.get_bpieces_left_col(col) == self.get_empty_spaces_col(col): # Assume-se que nunca vai ser <= 0
                row = 0
                while row < 10:
                    size = 0
                    while (row + size < 10) and\
                            (self.is_empty(self.get_value(row, col)) or self.is_boat_piece(self.get_value(row, col))):
                        size += 1

                    if size == 1:
                        if self.is_u_single(row, col):
                            boats_copy[size - 1] -= 1
                            if boats_copy[size - 1] < 0:
                                return 1
                            boats.append((row, col, size, 0, 0))
                        else:
                            self.add_hint(row, col, 'U')
                        col += size

                    elif size < 5:  # Assume [2,3,4]
                        boats_copy[size - 1] -= 1
                        if boats_copy[size - 1] < 0:
                            return 1
                        boats.append((row, col, size, 1, 0))
                        col += size

                    elif size > 4:
                        return 1

                    else:
                        col += 1

        if len(boats) == 0:
            return 2

        for boat in boats:
            row, col, size, orientation, hints = boat
            if self.place_boat(row, col, size, orientation, hints):
                return 1

        return 0

    def logic_away(self):

        self.flood_lines()
        while True:
            result = self.marshal_lines()
            if result == 0:
                self.flood_lines()
            elif result == 1:
                return 1
            elif result == 2:
                break

        return 0

    def place_boat(self, row: int, col: int, size: int, orientation: int, hints: int):
        """ Signigicado das hints é: peças que pertencem ao barco e ja se encontram no tabuleiro e ja têm os
        valores em consideracao no cálculo da informacao das linhas e colunas"""

        # TODO DELETE THIS
        print("----------------------BEFORE----------------------")
        print([row, col, size, orientation, hints])
        self.print_matrix_nf()
        self.print_rows_cols_limit()
        self.print_boats()
        self.print_hints()
        print("----------------------AFTER----------------------")

        # Verifica se o barco dado é valido
        if self.boat_not_valid(row, col, size, orientation, hints):
            return 1

        # Atualiza o número de barcos que faltam para o respetivo tamanho (nunca é < 0)
        self.update_boats_left(size)

        # Boat of size 1
        if size == 1:
            if self.place_boat_single(row, col):
                return 1
        # Vertical Orientation of size > 2
        elif orientation:
            if self.place_boat_long_vertical(row, col, size):
                return 1
        # Horizontal Orientation of size > 2
        else:
            if self.place_boat_long_horizontal(row, col, size):
                return 1

        # TODO DELETE THIS
        print([row, col, size, orientation, hints])
        self.print_matrix_nf()
        self.print_rows_cols_limit()
        self.print_boats()
        self.print_hints()

        return self

    def boat_not_valid(self, row: int, col: int, size: int, orientation: int, hints: int):
        """ Verifica se o barco dado como 'input' não viola regras triviais de barcos """

        # Verifica se o novo barco (vertical) não ultrapassa o limite da respetiva coluna
        # [As hints incluidas não são tidas em conta já que são contablizamos na criação]
        if orientation and (size - hints) > int(self.get_bpieces_left_col(col)):
            print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE > BPIECES LEFT [BUG]  \n\n")
            print(row, col, size, orientation, hints)
            return True

        # Verifica se o novo barco (horizontal) não ultrapassa o limite da respetiva linha
        # [As hints incluidas não são tidas em conta já que são contablizadas na criação]
        elif not orientation and (size - hints) > int(self.get_bpieces_left_row(row)):
            print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE MORE THAN BPIECES LEFT [BUG]  \n\n")
            print(row, col, size, orientation, hints)
            return True

        # Verifica se o novo barco (vertical) não se extende para fora do tabuleiro
        elif orientation and (row < 0 or size + row > 10):  # is vertical
            print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT THAT EXTENDS OUT OF THE BOARD [BUG]  \n\n")
            print(row, col, size, orientation, hints)
            return True

        # Verifica se o novo barco (horizontal) não se extende para fora do tabuleiro
        elif not orientation and (col < 0 or size + col > 10):  # is horizontal
            print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT THAT EXTENDS OUT OF THE BOARD [BUG]  \n\n")
            print(row, col, size, orientation, hints)
            return True

        # Verifica se o tamanho do barco respeita as regras (max size = 4)
        elif size > 4:
            print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE MORE THAN 4 [BUG]  \n\n")
            print("size =", size)
            print(row, col, size, orientation, hints)
            return True

        # Verifica se já foram colocados todos os barcos do tamanho dado como ‘input’
        elif self.boats[size - 1] <= 0:
            print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE ALREADY CLOSED [BUG]  \n\n")
            print("number of boats of the size =", self.boats[size - 1])
            print("size =", size)
            print(row, col, size, orientation, hints)
            return True

        return False

    def place_boat_single(self, row: int, col: int):

        if self.place_boat_line(row - 1, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
            return 1
        if self.place_boat_line(row, col, 'c', 0):  # [ '.' '.' '.'] -> [ 'w' 'c' 'w' ]
            return 1
        if self.place_boat_line(row + 1, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
            return 1

    def place_boat_long_vertical(self, row: int, col: int, size: int):

        if self.place_boat_line(row - 1, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
            return 1
        if self.place_boat_line(row, col, 't', 0):  # [ '.' '.' '.'] -> [ 'w' 't' 'w' ]
            return 1
        if self.place_boat_line(row + (size - 1), col, 'b', 0):  # [ '.' '.' '.'] -> [ 'w' 'b' 'w' ]
            return 1
        if self.place_boat_line(row + size, col, 'w', 0):  # [ '.' '.' '.'] -> [ 'w' 'w' 'w' ]
            return 1

        for i in range(size - 2):
            if self.place_boat_line(row + 1 + i, col, 'm', 0):  # [ '.' '.' '.'] -> [ 'w' 'm' 'w' ]
                return 1

    def place_boat_long_horizontal(self, row: int, col: int, size: int):

        if self.place_boat_line(row, col - 1, 'w', 1):  # [ '.' '.' '.']^T -> [ 'w' 'w' 'w' ]^T
            return 1
        if self.place_boat_line(row, col, 'l', 1):  # [ '.' '.' '.']^T -> [ 'w' 'l' 'w' ]^T
            return 1
        if self.place_boat_line(row, col + (size - 1), 'r', 1):  # [ '.' '.' '.']^T -> [ 'w' 'r' 'w' ]^T
            return 1
        if self.place_boat_line(row, col + size, 'w', 1):  # [ '.' '.' '.']^T -> [ 'w' 'w' 'w' ]^T
            return 1

        for i in range(size - 2):
            if self.place_boat_line(row, col + 1 + i, 'm', 1):  # [ '.' '.' '.']^T -> [ 'w' 'm' 'w' ]^T
                return 1

    def place_boat_line(self, row: int, col: int, piece: str, direction: int):

        water_pieces = [-1, 1]

        if self.is_boat_piece(piece):
            if self.is_empty(self.get_value(row, col)):
                self.add_piece(row, col, piece)
            elif self.is_boat_piece(self.get_value(row, col)):
                if piece.upper() == self.get_value(row, col):
                    pass
                elif self.is_unknown_piece(self.get_value(row, col)):
                    self.change_tile(row, col, piece)
                else:
                    print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT PIECE ON TOP OF ANOTHER BOAT (Excluding Right Hints and Unknowns) [BUG?]  \n\n")
                    return 1
            elif self.is_water_piece(self.get_value(row, col)):
                print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT PIECE ON TOP OF WATER [BUG?]  \n\n")
                return 1
        elif self.is_water_piece(piece):
            water_pieces.append(0)

        new_row = row
        new_col = col
        for i in water_pieces:
            if direction:  # Itera sobre a mesma coluna
                new_row = row + i
            else:  # Itera sobre a mesma linha
                new_col = col + i

            if self.is_empty(self.get_value(new_row, new_col)):
                self.add_piece(new_row, new_col, 'w')
            elif not self.is_inside_board(new_row, new_col) or self.is_water_piece(self.get_value(new_row, new_col)):
                continue
            elif self.is_boat_piece(self.get_value(new_row, new_col)):
                print("\n\n ILLEGAL RESULT NODE -> CREATING A WATER ON TOP OF BOATS ALREADY FILLED TILES [BUG??]  \n\n")
                return 1

        return 0

    # ----------------------- Helper functions for Actions -----------------------

    def get_hint_based_actions(self):  # Retorna uma ou mais actions com um unico move

        hints = 1
        actions = []

        row, col, piece = self.get_first_hint()
        self.remove_hint(row, col, piece)

        if self.is_center_piece(piece):
            actions.append((row, col, 1, 0, hints))
            return actions

        elif self.is_top_piece(piece):
            for size in self.get_available_sizes():

                next_piece = self.get_value(row + size - 1, col)

                if next_piece in ('w', 'W', None, 'R', 'L', 'T', 'C'):
                    break

                elif self.is_empty(next_piece):
                    actions.append((row, col, size, 1, hints))
                    continue

                elif next_piece == 'B':
                    hints += 1
                    self.remove_hint(row + size - 1, col, next_piece)
                    actions.append((row, col, size, 1, hints))
                    return actions

                elif next_piece in ('M', 'U'):
                    hints += 1
                    self.remove_hint(row + size - 1, col, next_piece)
                    continue

        elif self.is_bot_piece(piece):
            for size in self.get_available_sizes():  # This e excludes size 1

                next_piece = self.get_value(row - size + 1, col)

                if next_piece in ('w', 'W', None, 'R', 'L', 'B', 'C'):
                    break

                elif self.is_empty(next_piece):
                    actions.append((row - size + 1, col, size, 1, hints))
                    continue

                elif next_piece == 'T':
                    hints += 1
                    self.remove_hint(row - size + 1, col, next_piece)
                    actions.append((row - size + 1, col, size, 1, hints))
                    return actions

                elif next_piece in ('M', 'U'):
                    hints += 1
                    self.remove_hint(row - size + 1, col, next_piece)
                    continue

        elif self.is_left_piece(piece):
            for size in self.get_available_sizes():  # This e excludes size 1

                next_piece = self.get_value(row, col + size - 1)

                if next_piece in ('w', 'W', None, 'L', 'T', 'B', 'C'):
                    break

                elif self.is_empty(next_piece):
                    actions.append((row, col, size, 0, hints))
                    continue

                elif next_piece == 'R':
                    hints += 1
                    self.remove_hint(row, col + size - 1, next_piece)
                    actions.append((row, col, size, 0, hints))
                    return actions

                elif next_piece in ('M', 'U'):
                    hints += 1
                    self.remove_hint(row, col + size - 1, next_piece)
                    continue

        elif self.is_right_piece(piece):
            for size in self.get_available_sizes():  # This e excludes size 1

                next_piece = self.get_value(row, col - size + 1)

                if next_piece in ('w', 'W', None, 'R', 'T', 'B', 'C'):
                    break

                elif self.is_empty(next_piece):
                    actions.append((row, col - size + 1, size, 0, hints))
                    continue

                elif next_piece == 'L':
                    hints += 1
                    self.remove_hint(row, col - size + 1, next_piece)
                    actions.append((row, col - size + 1, size, 0, hints))
                    return actions

                elif next_piece in ('M', 'U'):
                    hints += 1
                    self.remove_hint(row, col - size + 1, next_piece)
                    continue

        elif self.is_unknown_piece(piece):
            if self.is_u_single(row, col):
                actions.append((row, col, 1, 0, hints))
                return actions
            return 0

        elif self.is_middle_piece(piece):
            return 0

        return actions

    def get_guess_boats_row(self, row: int, size: int):

        actions = []
        hints = 0

        col = 0
        while col < 10:
            max_size = 0
            if self.is_empty(self.get_value(row, col)) or self.is_unknown_piece(self.get_value(row, col)):
                max_size = 1
                while self.is_empty(self.get_value(row, col + max_size)) or\
                        self.is_unknown_piece(self.get_value(row, col + max_size)) or\
                        self.is_middle_piece(self.get_value(row, col + max_size)):
                    if self.is_unknown_piece(self.get_value(row, col + max_size)) or\
                            self.is_middle_piece(self.get_value(row, col + max_size)):
                        hints += 1

                    max_size += 1

                if max_size >= size:
                    for delta in range(0, max_size - size):
                        actions.append((row, col + delta, size, 0, hints))

            col += max_size + 1

        return actions

    def get_guess_boats_col(self, col: int, size: int):

        actions = []
        hints = 0

        row = 0
        while row < 10:
            max_size = 0
            if self.is_empty(self.get_value(row, col)) or self.is_unknown_piece(self.get_value(row, col)):
                max_size = 1
                while self.is_empty(self.get_value(row, col + max_size)) or \
                        self.is_unknown_piece(self.get_value(row + max_size, col)) or \
                        self.is_middle_piece(self.get_value(row + max_size, col)):
                    if self.is_unknown_piece(self.get_value(row + max_size, col)) or \
                            self.is_middle_piece(self.get_value(row + max_size, col)):
                        hints += 1

                    max_size += 1

                if max_size >= size:
                    for delta in range(0, max_size - size):
                        actions.append((row + delta, col, size, 1, hints))

            row += max_size + 1

        return actions

    def get_guess_based_actions(self):  # Retorna uma ou mais actions com um unico move

        size = max(self.get_available_sizes())
        possible_rows = []
        possible_cols = []
        actions = []

        hints_rows = [0 for _ in range(10)]
        hints_cols = [0 for _ in range(10)]
        if not self.is_hints_empty():
            hints = self.get_all_hints()
            for hint in hints:
                row, col, piece = hint
                hints_rows[row] += 1
                hints_cols[col] += 1

        for coordinate in range(10):

            if int(self.get_bpieces_left_row(coordinate)) >= size - hints_rows[coordinate]:  # UNICAS ROWS POSSIVEIS
                possible_rows.append(coordinate)

            if int(self.get_bpieces_left_col(coordinate)) >= size - hints_cols[coordinate]:  # UNICAS COLS POSSIVEIS
                possible_cols.append(coordinate)

        # AGORA É SÓ VER DENTRO DESSAS QUAIS SÃO OS BOATS DE SIZE POSSIBEL, SE É QUE EXISTEM

        for row in possible_rows:
            actions.extend(self.get_guess_boats_row(row, size))
        for col in possible_cols:
            actions.extend(self.get_guess_boats_col(col, size))

        return actions

    # TODO ############################################## TO BE DELETED ##############################################

    def print_matrix_nf(self):
        for row in self.matrix:
            print(row)

    def print_rows_cols_limit(self):
        print('rows limit:')
        print(self.bpieces_left_row)
        print('cols limit:')
        print(self.bpieces_left_col)

    def print_rows_cols_available(self):
        print('rows available:')
        print(self.empty_spaces_row)
        print('cols available:')
        print(self.empty_spaces_col)

    def print_boats(self):

        print("Size 1:", self.boats[0], " Size 2:", self.boats[1], " Size 3:", self.boats[2], " Size 4:", self.boats[3])

    def print_hints(self):

        print("Hints:", self.unexplored_hints)

    def print_board(self):
        """Imprime o tabuleiro"""
        app = Application(self.matrix, self.bpieces_left_row, self.bpieces_left_col)
        app.mainloop()

    def print(self):
        for row in self.matrix:
            for cell in row:
                if cell == 'w':
                    print('.', end='')
                else:
                    print(cell, end='')
            print()

    # TODO ############################################## END ##############################################

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        super().__init__(BimaruState(board))

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a partir
        do estado passado como argumento. Retorna None quando nao consegue
        encontrar uma unica jogada para devolver como ação. Uma açãoo
        pode ser várias jogadas consecutivas caso uma das jogadas cause uma
        chain reaction obrigatória. A funcao action pode entao retornar varias
        actions e cada action pode ter varias jogadas em cadeia. A funcao result
        aceita então um tuplo de jogadas. OU SEJA UMA ACAO E UM TUPLO DE JOGADAS"""

        if state is None:
            return []

        if not state.get_board().is_hints_empty():
            actions = state.get_board().get_hint_based_actions()  # Retorna uma unica action com 1 move
            if type(actions) == list and len(actions) > 0:
                return actions
            if type(actions) == int:
                return []

        actions = state.get_board().get_guess_based_actions()  # Retorna varias actions com 1 move
        return actions

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""

        new_board = copy.deepcopy(state.get_board())
        row, col, size, orientation, hints = action

        if new_board.place_boat(action) or new_board.logic_away():
            return None

        return BimaruState(new_board)

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas conforme as regras do problema."""

        # Verifica se é um estado válido
        if state is None:
            return False

        # Verifica se todos os barcos foram colocados
        for size in range(1, 5):
            if state.get_board().get_boats_left(size) != 0:
                return False

        # Verifica se todas as colunas e linhas estão cheias e com o número de peças de barco correto
        for coordenada in range(10):
            if (state.get_board().get_bpieces_left_row(coordenada) != 0) and\
                (state.get_board().get_bpieces_left_col(coordenada) != 0) and\
                (state.get_board().get_empty_spaces_row(coordenada) != 0) and\
                    (state.get_board().get_empty_spaces_col(coordenada) != 0):
                return False

        return True

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    # TODO: outros metodos da classe

if __name__ == "__main__":
    # TODO:
    # Ler o ficheiro do standard input,
    # Usar uma técnica de procura para resolver a instância,
    # Retirar a solução a partir do nó resultante,
    # Imprimir para o standard output no formato indicado.

    myBoard = Board.parse_instance()

    myBoard.print_matrix_nf()

    print('\n')

    move1 = (3, 2, 1, 0, 1)
    move2 = (9, 5, 1, 0, 1)

    action = myBoard.get_hint_based_actions()
    row, col, size, orientation, hints = action

    newBoard = myBoard.place_boat(row, col, size, orientation, hints)

    newBoard.print_matrix_nf()

    pass
