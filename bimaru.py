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

from gui import Application


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
		self.rows = [] # barcos em falta na linha
		self.columns = [] # barcos em falta na coluna
		self.rows_pieces = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10] # peças em falta na linha
		self.columns_pieces = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10] # peças em falta na coluna


	def isValid(self, row: int, col: int):
		return 0 <= row <= 9 and 0 <= col <= 9

	def notEmpty(self, row: int, col: int):
		return self.matrix[row][col] != '.'

	def isPiece(self, row: int, col: int):
		return self.isValid(row,col) and (self.matrix[row][col] == 'M' or self.matrix[row][col] == 'U' or self.matrix[row][col] == 'T' or self.matrix[row][col] == 'B' or self.matrix[row][col] == 'C' or self.matrix[row][col] == 'L' or self.matrix[row][col] == 'R')

	def get_value(self, row: int, col: int) -> str:
		"""Devolve o valor na respetiva posição do tabuleiro."""
		if self.isValid(row, col) and self.notEmpty(row, col):
			return self.matrix[row][col] 
		else:
			return None

	def adjacent_vertical_values(self, row: int, col: int) -> (str, str):
		"""Devolve os valores imediatamente acima e abaixo,
		respectivamente."""
		return (self.get_value(row-1, col), self.get_value(row+1, col))

	def adjacent_horizontal_values(self, row: int, col: int) -> (str, str):
		"""Devolve os valores imediatamente à esquerda e à direita,
		respectivamente."""
		return (self.get_value(row, col-1), self.get_value(row, col+1))

	def get_water_positions(self, row:int, col: int, type: str):
		"""Retorna as posições da agua para uma determinada peça"""
		positions = [(row-1, col-1), (row-1, col), (row, col-1), (row+1, col+1), (row+1, col), (row, col+1), (row+1, col-1), (row-1, col+1)]
		if type == 'T':
			positions.pop(positions.index((row+1, col)))
		elif type == 'B':
			positions.pop(positions.index((row-1, col)))
		elif type == 'L':
			positions.pop(positions.index((row, col+1)))
		elif type == 'R':
			positions.pop(positions.index((row, col-1)))
		elif type == 'M':
			vertical = self.adjacent_vertical_values(row, col)
			horizontal = self.adjacent_horizontal_values(row,col)
			if vertical[0] == 'W' or vertical[1] == 'W' or (horizontal[0] != 'W' and horizontal[0] != None) or (horizontal[1] != 'W' and horizontal[1] != None):
				positions.pop(positions.index((row, col-1)))
				positions.pop(positions.index((row, col+1)))
			if horizontal[0] == 'W' or horizontal[1] == 'W' or (vertical[0] != 'W' and vertical[0] != None) or (vertical[1] != 'W' and vertical[1] != None):
				positions.pop(positions.index((row+1, col)))
				positions.pop(positions.index((row-1, col)))
			if horizontal == (None, None) and vertical == (None, None):
				positions.pop(positions.index((row, col-1)))
				positions.pop(positions.index((row, col+1)))
				positions.pop(positions.index((row+1, col)))
				positions.pop(positions.index((row-1, col)))
		elif type == 'U' or type == 'M':
			positions.pop(positions.index((row, col-1)))
			positions.pop(positions.index((row, col+1)))
			positions.pop(positions.index((row+1, col)))
			positions.pop(positions.index((row-1, col)))

		def valid_pos(pos):
			return self.isValid(pos[0], pos[1])
		positions = list(filter(valid_pos, positions))
		return positions
	
	def fill_water(self, cells):
		"""Preenche multiplas celas com água"""
		preencheu = False # retorna true se preencheu pelo menos 1 cela com água
		for cell in cells:
			row, col = cell
			if self.get_value(row,col) == None and self.isValid(row, col):
				self.matrix[row][col] = 'W'
				self.rows_pieces[row] -= 1
				self.columns_pieces[col] -= 1
				preencheu = True
		return preencheu
	
	def add_piece(self, row: int, col: int, type: str):
		"""Adiciona uma peça à cela correspondente"""
		if type == 'W':
			self.fill_water([(row, col)])
		else:
			self.matrix[row][col] = type
			self.rows[row] -= 1
			self.rows_pieces[row] -= 1
			self.columns[col] -= 1
			self.columns_pieces[col] -= 1

	

	def load_board(self):
		"""Carrega o jogo"""
		alterado = True
		while alterado:
			alterado = False
			# 1- Preenche celas cheias com água
			for i in range(10):
				if self.rows[i] == 0 and self.rows_pieces[i] != 0:
					self.fill_water([(i, j) for j in range(10)])
					alterado = True
				if self.columns[i] == 0 and self.columns_pieces[i] != 0:
					self.fill_water([(j, i) for j in range(10)])
					alterado = True
			# 2- Rodeia as peças com água
			for row in range(10):
				for col in range(10):
					if self.isPiece(row,col):
						if self.fill_water(self.get_water_positions(row,col,self.get_value(row,col))):
							alterado = True
			# 3- Adiciona peças temporarias aos TOP, BOTTOM, MIDDLE, LEFT e RIGHT
			for row in range(10):
				for col in range(10):
					value = self.get_value(row,col)
					horizontal = self.adjacent_horizontal_values(row,col)
					vertical = self.adjacent_vertical_values(row,col)
					if (value == 'T' and vertical[1] == None) or (value == 'M' and (horizontal[0] == None or horizontal[1] == None or horizontal[0] == 'W' or horizontal[1] == 'W') and vertical[1] == None):
						self.add_piece(row+1,col,'U')
						alterado = True
					if value == 'B' and vertical[0] == None or (value == 'M' and (horizontal[0] == None or horizontal[1] == None or horizontal[0] == 'W' or horizontal[1] == 'W') and vertical[0] == None):
						self.add_piece(row-1,col,'U')
						alterado = True
					if value == 'L' and horizontal[1] == None or (value == 'M' and (vertical[0] == None or vertical[1] == None or vertical[0] == 'W' or vertical[1] == 'W') and horizontal[1] == None):
						self.add_piece(row,col+1,'U')
						alterado = True
					if value == 'R' and horizontal[0] == None or (value == 'M' and (vertical[0] == None or vertical[1] == None or vertical[0] == 'W' or vertical[1] == 'W') and horizontal[0] == None):
						self.add_piece(row,col-1,'U')
						alterado = True
			# 4 - Adiciona peças temporarias a espaços onde só faltam essas para preencher
			for i in range(10):
				if self.rows[i] == self.rows_pieces[i] != 0:
					for j in range(10):
						if self.get_value(i,j) == None:
							self.add_piece(i,j,'U')
							alterado = True
				if self.columns[i] == self.columns_pieces[i] != 0:
					for j in range(10):
						if self.get_value(j,i) == None:
							self.add_piece(j,i,'U')
							alterado = True
			# 5 - Converte peças temporárias em peças permanentes
			for row in range(10):
				for col in range(10):
					value = self.get_value(row,col)
					if value == 'U':
						horizontal = self.adjacent_horizontal_values(row,col)
						vertical = self.adjacent_vertical_values(row,col)
						# A peça é TOP sse tem uma peça abaixo, e acima dela tem ou agua ou vazio
						if (vertical[1] == 'U' or vertical[1] == 'B' or vertical[1] == 'M') and (vertical[0] == 'W' or not self.isValid(row-1,col)):
							self.matrix[row][col] = 'T'
							alterado = True
						# A peça é BOTTOM sse tem uma peça acima, e abaixo dela tem ou agua ou vazio
						elif (vertical[0] == 'U' or vertical[0] == 'T' or vertical[0] == 'M') and (vertical[1] == 'W' or not self.isValid(row+1,col)):
							self.matrix[row][col] = 'B'
							alterado = True
						# A peça é LEFT sse tem uma peça à direita, e à esquerda dela tem ou agua ou vazio
						elif (horizontal[1] == 'U' or horizontal[1] == 'R' or horizontal[1] == 'M') and (horizontal[0] == 'W' or not self.isValid(row,col-1)):
							self.matrix[row][col] = 'L'
							alterado = True
						# A peça é RIGHT sse tem uma peça à esquerda, e à direita dela tem ou agua ou vazio
						elif (horizontal[0] == 'U' or horizontal[0] == 'L' or horizontal[0] == 'M') and (horizontal[1] == 'W' or not self.isValid(row,col+1)):
							self.matrix[row][col] = 'R'
							alterado = True
						# A peça é CENTER sse tem água ou vazio à volta dela
						elif (vertical[0] == 'W' or not self.isValid(row-1,col)) and (vertical[1] == 'W' or not self.isValid(row+1,col)) and (horizontal[0] == 'W' or not self.isValid(row,col-1)) and (horizontal[1] == 'W' or not self.isValid(row,col+1)):
							self.matrix[row][col] = 'C'
							alterado = True
						# A peça é MIDDLE sse tem peças acima e abaixo OU peças à direita e à esquerda
						elif (self.isPiece(row+1,col) and self.isPiece(row-1,col)) or (self.isPiece(row,col+1) and self.isPiece(row,col-1)):
							self.matrix[row][col] = 'M'
							alterado = True
				

	
	def print_board(self):
		"""Imprime o tabuleiro"""
		app = Application(self.matrix, self.rows, self.columns)
		app.mainloop()


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
			row = int(hint[0])
			col = int(hint[1])

			val = hint[2]
			board.add_piece(row,col,val)
		board.load_board()


		
		# faz o pre-processamento inicial

		#board.preload_board()
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
