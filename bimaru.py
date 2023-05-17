# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 120:
# 103468 Pedro Gomes
# 104156 Henrique Pimentel

import sys

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

    # TODO: outros metodos da classe


class Board:
    """Representação interna de um tabuleiro de Bimaru."""
    """ Tem uma matriz que serve para representação do board, 
    talvez mudar para 1 matriz e 2 tuplos ????"""

    def __init__(self):
        self.matrix = [['_' for _ in range(11)] for _ in range(11)]
        self.unflooded_pieces = []

    def get_value(self, row: int, col: int):
        """Devolve o valor na respetiva posição do tabuleiro. Se estiver
        fora retorna None, se não houver peca retorna '_' """

        if self.is_inside_board(row, col):
            return str(self.matrix[row][col])
        else:
            return None

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""

        return self.get_value(row - 1, col),self.get_value(row + 1, col)

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respetivamente. Para evitar comparacoes desnecessarias nao
        vamos verificar se os inputs nao passam da dimensao do board"""

        return self.get_value(row, col - 1), self.get_value(row, col + 1)

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) passado como argumento
        e retorna uma instância da classe Board."""

        board = Board()
        rows = sys.stdin.readline().split()
        columns = sys.stdin.readline().split()

        board.change_tile(10, 10, 'X')  # Soh para diferenciar dos locais sem pecas
        for i in range(10):
            board.change_tile(i, 10, rows[i + 1])
            board.change_tile(10, i, columns[i + 1])

        number_hints = sys.stdin.readline().split()
        for i in range(int(number_hints[0])):
            hint = sys.stdin.readline().split()
            board.add_piece(int(hint[1]), int(hint[2]), hint[3])

        board.flood_col_row()
        board.sort_unflooded()

        while True:
            initial_length = len(board.unflooded_pieces)  # Store the initial length of the list
            board.flood_unflooded_pieces()
            if len(board.unflooded_pieces) == initial_length:
                break

        return board

    # Outros metodos da classe---------------------------------------------------------------
    def change_tile(self, row, col, new_piece):
        """ Changes the value in the position (row,col) of the board's matrix."""
        self.matrix[row][col] = new_piece

    def add_piece(self, row, col, new_piece):
        """ Executes change_tile, but if it is a boat piece it updates the limit
        values for its row and column and adds water to nearby positions """

        self.change_tile(row, col, new_piece)
        if self.is_boat_piece(new_piece):
            self.update_limits(row, col)
            self.store_unflooded_piece(row, col, new_piece)

    def store_unflooded_piece(self, row, col, new_piece):
        self.unflooded_pieces.append((row, col, new_piece))

    def sort_unflooded(self):
        self.unflooded_pieces = sorted(self.unflooded_pieces, key=lambda x: x[2] == 'M')

    def limit_row(self, row):
        return self.matrix[row][10]

    def limit_column(self, col):
        return self.matrix[10][col]

    def update_limits(self, row, col):
        self.matrix[10][col] = str(int(self.matrix[10][col]) - 1)
        self.matrix[row][10] = str(int(self.matrix[row][10]) - 1)

    def is_boat_piece(self, piece):
        return piece.upper() in ['T', 'B', 'L', 'R', 'C', 'M']

    def is_water_piece(self, piece):
        return piece.upper() == 'W'

    def is_empty(self, piece):
        return piece == '_'

    def is_inside_board(self, row, col):
        return (0 <= row <= 9) and (0 <= col <= 9)

    def flood_unflooded_pieces(self):
        if not self.unflooded_pieces:
            return
        else:
            for x in self.unflooded_pieces[:]:
                self.flood_tiles(x[0], x[1], x[2])

    def flood_col_row(self):
        for i in range(10):
            if self.limit_row(i) == '0':
                for j in range(10):
                    if self.is_empty(self.get_value(i, j)):
                        self.change_tile(i, j, 'w')
            if self.limit_column(i) == '0':
                for j in range(10):
                    if self.is_empty(self.get_value(j, i)):
                        self.change_tile(j, i, 'w')

    def middle_has_orientation(self, row, col):
        """
        Vai verificar se existe uma possivel orientacao da middle piece
        que seja obrigatoria. Verifica obrigatoriedade se uma row/column tem
        espaco para duas pecas, mas a outra nao.
        :return: 0 se nao houver orientacao clara, 1 se a orientacao for
        vertical, 2 se a orientacao for horizontal
        """

        if any(value in ('w', 'W', None) for value in self.adjacent_horizontal_values(row, col)):
            return 1
        elif any(value in ('w', 'W', None) for value in self.adjacent_vertical_values(row, col)):
            return 2
        elif int(self.limit_row(row)) <= 1 < int(self.limit_column(col)):
            return 1
        elif int(self.limit_column(col)) <= 1 < int(self.limit_row(row)):
            return 2
        else:
            return 0

    def middle_is_vertical(self, row, col):
        return self.middle_has_orientation(row, col) == 1

    def middle_is_horizontal(self, row, col):
        return self.middle_has_orientation(row, col) == 2

    def flood_tiles(self, row, col, piece):

        adjacent_coordinates = self.get_adjacent_coordinates(row, col, piece)

        if not (adjacent_coordinates is None):
            for x in adjacent_coordinates:
                if self.is_inside_board(x[0], x[1]):
                    self.change_tile(x[0], x[1], 'w')
            self.unflooded_pieces.remove((row, col, piece))

        return

    def get_adjacent_coordinates(self, row, col, piece):

        if piece == 'C':
            adjacent_coords = [(row + i, col + j) for i in range(-1, 2) for j in range(-1, 2)
                               if not (i == 0 and j == 0)]
            return tuple(adjacent_coords)

        elif piece == 'T':
            adjacent_coords = [(row + i, col + j) for i in range(-1, 3) for j in range(-1, 2)
                               if not (i == 0 and j == 0) and not (i == 1 and j == 0)
                               and not (i == 2 and j == 0)]
            return tuple(adjacent_coords)

        elif piece == 'B':
            adjacent_coords = [(row + i, col + j) for i in range(-2, 2) for j in range(-1, 2)
                               if not (i == 0 and j == 0) and not (i == -1 and j == 0)
                               and not (i == -2 and j == 0)]
            return tuple(adjacent_coords)

        elif piece == 'L':
            adjacent_coords = [(row + i, col + j) for i in range(-1, 2) for j in range(-1, 3)
                               if not (i == 0 and j == 0) and not (i == 0 and j == 1)
                               and not (i == 0 and j == 2)]
            return tuple(adjacent_coords)

        elif piece == 'R':
            adjacent_coords = [(row + i, col + j) for i in range(-1, 2) for j in range(-2, 2)
                               if not (i == 0 and j == 0) and not (i == 0 and j == -1)
                               and not (i == 0 and j == -2)]
            return tuple(adjacent_coords)

        elif piece == 'M':
            if self.middle_is_vertical(row, col):
                adjacent_coords = [(row + i, col + j) for i in range(-1, 2) for j in range(-1, 2)
                                   if not (j == 0)]
                return tuple(adjacent_coords)

            elif self.middle_is_horizontal(row, col):
                adjacent_coords = [(row + i, col + j) for i in range(-1, 2) for j in range(-1, 2)
                                   if not (i == 0)]
                return tuple(adjacent_coords)



    def print_matrix_nf(self):
        for row in self.matrix:
            print(row)


class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        # TODO
        pass

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass

    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

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

    pass
