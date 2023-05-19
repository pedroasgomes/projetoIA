# bimaru.py: Template para implementação do projeto de Inteligência Artificial 2022/2023.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 00:
# 00000 Nome1
# 00000 Nome2

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
	def __init__(self):
		self.matrix = [['.' for _ in range(10)] for _ in range(10)]
		self.boats = []
		self.rows = []
		self.columns = []

	def get_value(self, row: int, col: int) -> str:
		"""Devolve o valor na respetiva posição do tabuleiro."""
		if 0 <= row <= 9 and 0 <= col <= 9 and self.matrix[row][col] != '.':
			return self.matrix[row][col] 
		else:
			return None

	def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
		"""Devolve os valores imediatamente acima e abaixo,
		respectivamente."""
		values = []
		if 0 <= row-1 <= 9 and self.matrix[row-1][col] != '.':
			values.append(self.matrix[row-1][col])
		else:
			values.append(None)
		if 0 <= row+1 <= 9 and self.matrix[row+1][col] != '.':
			values.append(self.matrix[row+1][col])
		else:
			values.append(None)
		return tuple(values)

	def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
		"""Devolve os valores imediatamente à esquerda e à direita,
		respectivamente."""
		values = []
		if 0 <= col-1 <= 9 and self.matrix[row][col-1] != '.':
			values.append(self.matrix[row][col-1])
		else:
			values.append(None)
		if 0 <= col+1 <= 9 and self.matrix[row][col+1] != '.':
			values.append(self.matrix[row][col+1])
		else:
			values.append(None)
		return tuple(values)

	
	def print_board(self):
		"""Imprime o tabuleiro"""
		i = 0
		for line in self.matrix:
			print(' '.join(line) + ' ' + str(self.rows[i]))
			i += 1
		list_columns = [str(num) for num in self.columns]
		print(' '.join(list_columns))


	@staticmethod
	def parse_instance():
		"""Lê o test do standard input (stdin) que é passado como argumento
		e retorna uma instância da classe Board."""
		board = Board()
		board.rows = [int(i) for i in sys.stdin.readline().split()[1:]]
		board.columns = [int(i) for i in sys.stdin.readline().split()[1:]]
		hints = int(sys.stdin.readline())
		for i in range(hints):
			hint = sys.stdin.readline().split()[1:]
			board.matrix[int(hint[0])][int(hint[1])] = hint[2]
			
		board.print_board()
		return board

	# TODO: outros metodos da classe


class Bimaru(Problem):
	def __init__(self, board: Board):
		"""O construtor especifica o estado inicial."""
		super().__init__(BimaruState(board))

	def actions(self, state: BimaruState):
		"""Retorna uma lista de ações que podem ser executadas a
		partir do estado passado como argumento."""
		# Ações que podem ser tomada:
		# - verifica se pode pôr barcos
		# - 
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

	board = Board().parse_instance()

	# TODO:

	# Usar uma técnica de procura para resolver a instância,
	# Retirar a solução a partir do nó resultante,
	# Imprimir para o standard output no formato indicado.
