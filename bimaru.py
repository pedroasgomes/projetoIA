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
        self.matrix = matrix = [['_' for _ in range(11)] for _ in range(11)]

    def get_value(self, row: int, col: int) -> str:
        """Devolve o valor na respetiva posição do tabuleiro."""
        return str(self.matrix[row][col])

    def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente acima e abaixo,
        respectivamente."""

        output = ()

        output = output + (None,) if row == 0 \
            else output + (self.get_value(row - 1, col),)

        output = output + (None,) if row == 9 \
            else output + (self.get_value(row + 1, col),)

        return output

    def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
        """Devolve os valores imediatamente à esquerda e à direita,
        respetivamente. Para evitar comparacoes desnecessarias nao
        vamos verificar se os inputs nao passam da dimensao do board"""

        output = ()

        output = output + (None,) if col == 0 \
            else output + (self.get_value(row, col - 1),)

        output = output + (None,) if col == 9 \
            else output + (self.get_value(row, col + 1),)

        return output

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
            board.change_tile(int(hint[1]), int(hint[2]), hint[3])
            board.flood_tiles(int(hint[1]), int(hint[2]), hint[3])







        return board

    # Outros metodos da classe
    def flood_tiles(self, row, col, piece):
        if piece == "W":
            return
        elif piece == "C":
            pass
        elif piece == "M":
            pass
        elif piece == "T":
            pass
        elif piece == "B":
            pass
        elif piece == "L":
            pass
        elif piece == "R":
            pass

    def change_tile(self, row, col, new_piece): # Accepts None as a piece but does nothing
        self.matrix[row][col] = new_piece

    def piece_limit_row(self, row):
        return self.get_value(row, 10)

    def piece_limit_column(self, col):
        return self.get_value(10, col)

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

    myBoard = Board()
    myBoard = myBoard.parse_instance()
    myBoard.print_matrix_nf()
    print(myBoard.adjacent_horizontal_values(0,0))
    print(myBoard.adjacent_vertical_values(0, 0))

    pass
