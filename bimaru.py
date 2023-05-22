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

    #TODO ############################################## ILEGAL ##############################################
    def get_board(self):
        return self.board
    # TODO ############################################## ILEGAL ##############################################

class Board:
    """Representação interna de um tabuleiro de Bimaru.
    Tem uma matriz que serve para representação do board e
    uma lista das peças dadas nas hints """

    def __init__(self):
        self.matrix = [['.' for _ in range(10)] for _ in range(10)]
        self.bpieces_left_row = []
        self.bpieces_left_col = []
        self.empty_spaces_row = ['10' for _ in range(10)]
        self.empty_spaces_col = ['10' for _ in range(10)]
        self.boats = [4,3,2,1]      # Where self.boats[size-1] = número de barcos que faltam por de tamanho 'size'
        self.unexplored_hints = []

    def get_value(self, row: int, col: int):
        """Devolve o valor na respetiva posição do tabuleiro. Se estiver
        fora retorna None, se não houver peca retorna '_' """

        if self.is_inside_board(row, col):
            return str(self.matrix[row][col])
        else:
            return None

    def adjacent_vertical_values(self, row: int, col: int):
        """Devolve os valores imediatamente acima e abaixo,
        respetivamente. Devolve None se estiver fora do tabuleiro,
        devolve '.' se nao houver peca"""

        return self.get_value(row - 1, col), self.get_value(row + 1, col)

    def adjacent_horizontal_values(self, row: int, col: int):
        """Devolve os valores imediatamente à esquerda e à direita,
        respetivamente. Devolve None se estiver fora do tabuleiro,
        devolve '.' se nao houver peca"""

        return self.get_value(row, col - 1), self.get_value(row, col + 1)

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) passado como argumento
        e retorna uma instância da classe Board."""

        board = Board()
        rows = sys.stdin.readline().split()
        columns = sys.stdin.readline().split()

        for i in range(10):
            board.bpieces_left_row.append(rows[i + 1])            # Guarda o número total de peças por colocar na row[i]
            board.bpieces_left_col.append(columns[i + 1])      # Guarda o número total de peças por colocar na col[i]

        number_hints = sys.stdin.readline().split()
        for j in range(int(number_hints[0])):
            hint = sys.stdin.readline().split()
            board.add_hint(int(hint[1]), int(hint[2]), hint[3])
        board.sort_unexplored()                             # Vai meter hints com M no fim da queue

        board.flood_lines()  # Vai preencher colunas e rows a 0 com 'w'

        return board

    # Outros metodos da classe---------------------------------------------------------------

    # Metodos para o parse

    # TODO ############################################## GETTERS E SETTER COM LOGICA ##############################################

    def change_tile(self, row, col, piece):

        self.matrix[row][col] = piece

    def add_piece(self, row, col, piece):

        self.change_tile(row, col, piece)
        self.update_empty_spaces(row, col)
        if self.is_boat_piece(piece):
            self.update_bpieces_left(row, col)

    def add_hint(self, row, col, piece):

        self.change_tile(row, col, piece)
        self.store_unexplored_hint(row, col, piece)

    def store_unexplored_hint(self, row, col, new_piece):
        self.unexplored_hints.append((row, col, new_piece))

    def remove_unexplored_hint(self, row, col, piece):
        self.unexplored_hints.remove((row, col, piece))

    def sort_unexplored(self):
        """ Coloca pecas 'M' no fim da queue jah que essas pecas podem nao ter
        orientacao e podem aumentar a ramificacao desnecessariamente."""
        self.unexplored_hints = sorted(self.unexplored_hints, key=lambda x:(x[2] != 'C', x[2] == 'M'))

    def is_unexplored_empty(self):
        return not self.unexplored_hints

    def get_boats_left(self, size):
        return self.boats[size - 1]

    def get_bpieces_left_row(self, row):
        return self.bpieces_left_row[row]

    def get_bpieces_left_col(self, col):
        return self.bpieces_left_col[col]

    def get_empty_spaces_row(self, row):
        return self.empty_spaces_row[row]

    def get_empty_spaces_col(self, col):
        return self.empty_spaces_col[col]

    def update_boats_left(self, size):
        self.boats[size - 1] -= 1

    def update_bpieces_left(self, row, col):
        self.bpieces_left_row[row] = str(int(self.bpieces_left_row[row]) - 1)
        self.bpieces_left_col[col] = str(int(self.bpieces_left_col[col]) - 1)

    def update_empty_spaces(self, row, col):
        self.empty_spaces_row[row] = str(int(self.empty_spaces_row[row]) - 1)
        self.empty_spaces_col[col] = str(int(self.empty_spaces_col[col]) - 1)

    def flood_lines(self):
        for i in range(10):
            if self.get_bpieces_left_row(i) == '0':
                for j in range(10):
                    if self.is_empty(self.get_value(i, j)):
                        self.add_piece(i, j, 'w')

            if self.get_bpieces_left_col(i) == '0':
                for j in range(10):
                    if self.is_empty(self.get_value(j, i)):
                        self.add_piece(j, i, 'w')

    # TODO ############################################## STATIC ##############################################

    def is_inside_board(self, row, col):
        return (0 <= row <= 9) and (0 <= col <= 9)

    def is_empty(self, piece):
        return piece == '.'

    def is_boat_piece(self, piece):
        return piece.upper() in ['T', 'B', 'L', 'R', 'C', 'M']

    def is_water_piece(self, piece):
        return piece.upper() == 'W'

    def is_middle_piece(self, piece):
        return piece.upper() == 'M'

    # Metodos especificos para fora da classe State

    # TODO ############################################## ACTIONS ##############################################

    def get_deterministic_action(self):  # Retorna uma unica action com 1 ou mais moves
        pass




    def get_hint_based_action(self):  # Retorna uma unica action com 1 move
        pass




    def get_guess_based_actions(self): # Retorna uma ou mais actions com um unico move
        pass

    # TODO ############################################## RESULT ##############################################


    def place_boats(self, action):
        """ Returns a copy of the initial state with the adition
        of the new boat. If the boat is impossible (it violates
        the rules) the return is instead None. """
        # TODO THIS FUNCTION WILL NOT RETURN NONE IF USE THE CAN_BOAT_FIT

        for move in action: #REMOVER NA ITERACAO FINAL

            if move[3] and move[2] > int(self.get_bpieces_left_col(move[1])): #is vertical
                print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE MORE THAN BPIECES LEFT (v) [BUG]  \n\n")
                return None

            elif move[3] and move[2] > int(self.get_bpieces_left_row(move[0])):  # is horizontal
                print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE MORE THAN BPIECES LEFT (h) [BUG]  \n\n")
                return None

            elif move[2] > 4:
                print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE MORE THAN 4 [BUG]  \n\n")
                return None

            elif not self.get_boats_left(move[2]):
                print("\n\n ILLEGAL RESULT NODE -> CREATING A BOAT OF SIZE ALREADY CLOSED [BUG]  \n\n")
                return None

        new_state = copy.deepcopy(self)

        for move in action:

            new_state.update_boats_left(move[2])

            if move[2] == 1:
                if new_state.place_boat_single(move[0], move[1]):
                    return None
            elif move[3]:                                           # Vertical Orientation
                if new_state.place_boat_long_vertical(move[0], move[1], move[2]):
                    return None
            else:                                                        # Horizontal Orientation
                if new_state.place_boat_long_horizontal(move[0], move[1], move[2]):
                    return None

        new_state.flood_lines()

        return new_state

    def place_boat_single(self, row, col):

        if self.place_boat_line(row - 1, col, 'w', 0):
            return 1
        if self.place_boat_line(row, col, 'c', 0):
            return 1
        if self.place_boat_line(row + 1, col, 'w', 0):
            return 1

    def place_boat_long_vertical(self, row, col, size):

        if self.place_boat_line(row - 1, col, 'w', 0):
            return 1
        if self.place_boat_line(row, col, 't', 0):
            return 1
        if self.place_boat_line(row + (size - 1), col, 'b', 0):
            return 1
        if self.place_boat_line(row + size, col, 'w', 0):
            return 1

        for i in range(size-2):
            if self.place_boat_line(row + 1 + i, col, 'm', 0):
                return 1

    def place_boat_long_horizontal(self, row, col, size):

        if self.place_boat_line(row, col - 1, 'w', 1):
            return 1
        if self.place_boat_line(row, col, 'l', 1):
            return 1
        if self.place_boat_line(row, col + (size - 1), 'r', 1):
            return 1
        if self.place_boat_line(row, col + size, 'w', 1):
            return 1

        for i in range(size-2):
            if self.place_boat_line(row, col + 1 + i, 'm', 1):
                return 1

    def place_boat_line(self, row, col, piece, direction):

        water_pieces = [-1, 1]

        if self.is_water_piece(piece):
            water_pieces.append(0)

        elif not self.is_empty(self.get_value(row, col)):
            if self.get_value(row, col).lower() != piece:
                print("\n\n ILLEGAL RESULT NODE -> CREATING A BOATS ON ALREADY FILLED TILES (Excluding Hints of the Boat in Question) [BUG?]  \n\n")
                return 1
            else: # CASO EM QUE A HINT COINCIDE COM O BARCO
                self.update_bpieces_left(row, col)
                self.update_empty_spaces(row, col)
                self.remove_unexplored_hint(row, col, str(piece).upper())

        else:
            self.add_piece(row, col, piece)

        for i in water_pieces:
            if direction:               # Columns (of size 3)
                new_row = row + i
                new_col = col
            else:                       # Rows (of size 3)
                new_row = row
                new_col = col + i

            if not self.is_inside_board(new_row, new_col) or \
                    self.is_water_piece(self.get_value(new_row, new_col)):
                continue

            if self.is_boat_piece(self.get_value(new_row, new_col)):
                print("\n\n ILLEGAL RESULT NODE -> CREATING A WATER ON ALREADY FILLED TILES (Excluding water e outofbounds) [BUG??]  \n\n")
                return 1

            self.add_piece(new_row, new_col, 'w')

    # TODO ############################################## GOAL ##############################################

    def all_boats_placed(self):
        """ Retorna False se ainda houver boats de tamanho size
         por colocar. Retorna true se todos os boats de todos os
         tamanhos ja tenham sido colocados. """
        for size in range(1,5):
            if self.get_boats_left(size) != 0:
                return False
        return True


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

    # TODO ############################################## END ##############################################
    # TODO ############################################## END ##############################################
    # TODO ############################################## END ##############################################

class Bimaru(Problem):
    def __init__(self, board: Board):
        """O construtor especifica o estado inicial."""
        super().__init__(board)

    def actions(self, state: BimaruState):
        """Retorna uma lista de ações que podem ser executadas a partir
        do estado passado como argumento. Retorna None quando nao consegue
        encontrar uma unica jogada para devolver como ação. Uma açãoo
        pode ser várias jogadas consecutivas caso uma das jogadas cause uma
        chain reaction obrigatória. A funcao action pode entao retornar varias
        actions e cada action pode ter varias jogadas em cadeia. A funcao result
        aceita então um tuplo de jogadas. OU SEJA UMA ACAO E UM TUPLO DE JOGADAS"""

        actions = state.self.get_board().get_deterministic_action() # Retorna uma unica action com 1 ou mais moves
        if actions:
            return actions

        actions = state.self.get_board().get_hint_based_action() # Retorna uma unica action com 1 move
        if actions:
            return actions

        actions = state.self.get_board().get_guess_based_actions() # Retorna varias actions com 1 move
        if actions:
            return actions

        return None

        #TODO RETORNA LISTA DE ACTIONS-----------


    def result(self, state: BimaruState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        new_board = state.get_board().place_boats(action)

        if new_board is None:
            return None
        else:
            return BimaruState(new_board)

    def goal_test(self, state: BimaruState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        if state.get_board().all_boats_placed():
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
    print(myBoard.unexplored_hints)
    myBoard.print_rows_cols_limit()
    myBoard.print_rows_cols_available()

    print('\n')
    move1 = (2, 2, 4, 1)
    move2= (2, 0, 4, 1)
    action = [move1]
    newBoard = myBoard.place_boats(action)

    newBoard.print_matrix_nf()
    print(newBoard.unexplored_hints)
    newBoard.print_rows_cols_limit()
    newBoard.print_rows_cols_available()


    pass