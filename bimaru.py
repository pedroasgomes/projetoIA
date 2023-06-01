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
		self.hints = []

		self.unclosed_rows = list(range(10))
		self.unclosed_columns = list(range(10))

	def __str__(self):
		result = ""
		for hint in self.hints:
			self.matrix[hint[0]][hint[1]] = 'C'
		for row in self.matrix:
			for cell in row:
				if cell == 'w':
					result += '.'
				else:
					result += cell
			result += '\n'
		return result[:-1]

	def copy_board(self):
		board = Board()

		for i in range(10):
			board.matrix[i] = self.matrix[i][:]

		board.unexplored_hints = self.unexplored_hints[:]
		board.bpieces_left_row = self.bpieces_left_row[:]
		board.bpieces_left_col = self.bpieces_left_col[:]
		board.empty_spaces_row = self.empty_spaces_row[:]
		board.empty_spaces_col = self.empty_spaces_col[:]
		board.boats = self.boats[:]  # Where self.boats[size-1] = número de barcos que faltam por de tamanho 'size'
		board.hints = self.hints[:]
		board.unclosed_rows = self.unclosed_rows[:]
		board.unclosed_columns = self.unclosed_columns[:]

		return board

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
			if self.is_empty(self.get_value(row, col)):
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
			if hint[3] == 'C':
				board.hints.append((int(hint[1]), int(hint[2])))
				
		board.sort_hints()  # Vai meter hints com M no fim da queue

		board.logic_away()  # TODO OOOOOOOOOOOOOOOOOO 1337

		return board

	@staticmethod
	def is_inside_board(row: int, col: int):
		return (0 <= row <= 9) and (0 <= col <= 9)

	@staticmethod
	def is_hint_piece(piece: str):
		if type(piece) == str:
			return piece.isupper()
		else:
			return 0

	@staticmethod
	def is_new_piece(piece: str):
		if type(piece) == str:
			return piece.islower()
		else:
			return 0

	@staticmethod
	def is_empty(piece: str):
		return piece == '.'

	@staticmethod
	def is_water_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'W'
		else:
			return 0

	@staticmethod
	def is_boat_piece(piece: str):
		if type(piece) == str:
			return piece.upper() in ['C', 'T', 'B', 'L', 'R', 'M', 'U']
		else:
			return 0

	@staticmethod
	def is_center_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'C'
		else:
			return 0

	@staticmethod
	def is_top_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'T'
		else:
			return 0

	@staticmethod
	def is_bot_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'B'
		else:
			return 0

	@staticmethod
	def is_left_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'L'
		else:
			return 0

	@staticmethod
	def is_right_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'R'
		else:
			return 0

	@staticmethod
	def is_middle_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'M'
		else:
			return 0

	@staticmethod
	def is_unknown_piece(piece: str):
		if type(piece) == str:
			return piece.upper() == 'U'
		else:
			return 0

	# =========================== Upper level functions ===========================

	def flood_lines(self):

		for row in list(self.get_unclosed_rows()):
			if self.get_bpieces_left_row(row) == '0':
				self.add_closed_row(row)
				for col in range(10):
					if self.is_empty(self.get_value(row, col)):
						self.add_piece(row, col, 'w')

		for col in list(self.get_unclosed_columns()):
			if self.get_bpieces_left_col(col) == '0':
				self.add_closed_column(col)
				for row in range(10):
					if self.is_empty(self.get_value(row, col)):
						self.add_piece(row, col, 'w')

	def marshal_lines(self):

		boats = []
		boats_copy = self.boats[:]
		new_hints = []

		for row in self.get_unclosed_rows():
			if self.get_bpieces_left_row(row) == self.get_empty_spaces_row(row):  # Assume-se que nunca vai ser <= 0
				col = 0
				while col < 10:
					size = 0
					hints = 0
					while (col + size < 10) and (self.is_empty(self.get_value(row, col + size)) or \
							(self.is_middle_piece(self.get_value(row, col + size)) and (self.is_hint_piece(self.get_value(row, col + size)))) or\
							self.is_unknown_piece(self.get_value(row, col + size))):
						if self.is_middle_piece(self.get_value(row, col + size)) or self.is_unknown_piece(self.get_value(row, col + size)):
							hints += 1
						size += 1

					if size == 0:
						col += 1

					elif size == 1:
						if self.is_empty(self.get_value(row, col)):
							if self.is_u_single(row, col):
								boats_copy[size - 1] -= 1
								if boats_copy[size - 1] < 0:
									return 1
								boats.append((row, col, size, 0, hints))
							else:
								new_hints.append((row, col, 'U'))
						if self.is_unknown_piece(self.get_value(row, col)):
							if self.is_u_single(row, col):
								boats_copy[size - 1] -= 1
								if boats_copy[size - 1] < 0:
									return 1
								boats.append((row, col, size, 0, hints))

						col += size

					elif 1 < size < 5:  # Assume [2,3,4]
						# TODO CASO EM QUE SIZE == 2 E EH tMMp por exemplo
						if size == 2 and self.is_middle_piece(self.get_value(row, col)) and self.is_middle_piece(self.get_value(row, col + 1)):
							continue
						else:
							boats_copy[size - 1] -= 1
							if boats_copy[size - 1] < 0:
								return 1
							boats.append((row, col, size, 0, hints))
						col += size

					elif size > 4:
						return 1

		for col in self.get_unclosed_columns():
			if self.get_bpieces_left_col(col) == self.get_empty_spaces_col(col):  # Assume-se que nunca vai ser <= 0
				row = 0
				while row < 10:
					size = 0
					hints = 0
					while (row + size < 10) and (self.is_empty(self.get_value(row + size, col)) or\
							(self.is_middle_piece(self.get_value(row + size, col)) and self.is_hint_piece(self.get_value(row + size, col))) or\
							self.is_unknown_piece(self.get_value(row + size, col))):
						if self.is_middle_piece(self.get_value(row + size, col)) or self.is_unknown_piece(self.get_value(row + size, col)):
							hints += 1
						size += 1
					if size == 0:
						row += 1

					elif size == 1:
						if self.is_empty(self.get_value(row, col)):
							if any(element[0] == row and element[1] == col for element in boats):
								pass
							elif self.is_u_single(row, col):
								boats_copy[size - 1] -= 1
								if boats_copy[size - 1] < 0:
									return 1
								boats.append((row, col, size, 0, hints))
							else:
								new_hints.append((row, col, 'U'))
						if self.is_unknown_piece(self.get_value(row, col)):
							if self.is_u_single(row, col):
								boats_copy[size - 1] -= 1
								if boats_copy[size - 1] < 0:
									return 1
								boats.append((row, col, size, 0, hints))
						row += size

					elif 1 < size < 5:  # Assume [2,3,4]
						# TODO CASO EM QUE SIZE == 2 E EH tMMp por exemplo
						if size == 2 and self.is_middle_piece(self.get_value(row, col)) and self.is_middle_piece(self.get_value(row + 1, col)):
							continue
						else:
							boats_copy[size - 1] -= 1
							if boats_copy[size - 1] < 0:
								return 1
							boats.append((row, col, size, 1, hints))
							row += size

					elif size > 4:
						return 1

		if len(boats) == 0:
			if len(new_hints) == 0:
				return 2
			else:
				for new_hint in new_hints:
					row, col, piece = new_hint
					self.add_hint(row, col, piece)

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

		return 0

	def boat_not_valid(self, row: int, col: int, size: int, orientation: int, hints: int):
		""" Verifica se o barco dado como 'input' não viola regras triviais de barcos """

		# Verifica se o novo barco (vertical) não ultrapassa o limite da respetiva coluna
		# [As hints incluidas não são tidas em conta já que são contablizamos na criação]
		if orientation and (size - hints) > int(self.get_bpieces_left_col(col)):
			return True

		# Verifica se o novo barco (horizontal) não ultrapassa o limite da respetiva linha
		# [As hints incluidas não são tidas em conta já que são contablizadas na criação]
		elif not orientation and (size - hints) > int(self.get_bpieces_left_row(row)):
			return True

		# Verifica se o novo barco (vertical) não se extende para fora do tabuleiro
		elif orientation and (row < 0 or size + row > 10):  # is vertical
			return True

		# Verifica se o novo barco (horizontal) não se extende para fora do tabuleiro
		elif not orientation and (col < 0 or size + col > 10):  # is horizontal
			return True

		# Verifica se o tamanho do barco respeita as regras (max size = 4)
		elif size > 4:
			return True

		# Verifica se já foram colocados todos os barcos do tamanho dado como ‘input’
		elif self.boats[size - 1] <= 0:
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
					self.remove_hint(row, col, self.get_value(row, col))
					pass
				elif self.is_unknown_piece(self.get_value(row, col)):
					self.remove_hint(row, col, self.get_value(row, col))
					self.change_tile(row, col, piece)
				else:
					return 1
			elif self.is_water_piece(self.get_value(row, col)):
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

			if not self.is_inside_board(new_row, new_col) or self.is_water_piece(self.get_value(new_row, new_col)):
				continue
			if self.is_empty(self.get_value(new_row, new_col)):
				self.add_piece(new_row, new_col, 'w')
			elif self.is_boat_piece(self.get_value(new_row, new_col)):
				return 1

		return 0

	# ----------------------- Helper functions for Actions -----------------------

	def get_hint_based_actions(self):  # Retorna uma ou mais actions com um unico move

		hints = 1
		actions = []

		for hint in self.get_all_hints():
			row, col, piece = hint

			if self.is_center_piece(piece):
				actions.append((row, col, 1, 0, hints))
				return actions

			elif self.is_top_piece(piece):
				for size in self.get_available_sizes():

					if size == 1:
						continue

					next_piece = self.get_value(row + size - 1, col)

					if next_piece in ('w', 'W', None, 'R', 'L', 'T', 'C'):
						break

					elif self.is_empty(next_piece):
						actions.append((row, col, size, 1, hints))
						continue

					elif next_piece == 'B':
						hints += 1
						actions.append((row, col, size, 1, hints))
						return actions

					elif next_piece in ('M', 'U'):
						hints += 1
						continue

				return actions

			elif self.is_bot_piece(piece):
				for size in self.get_available_sizes():  # This e excludes size 1

					if size == 1:
						continue

					next_piece = self.get_value(row - size + 1, col)

					if next_piece in ('w', 'W', None, 'R', 'L', 'B', 'C'):
						break

					elif self.is_empty(next_piece):
						actions.append((row - size + 1, col, size, 1, hints))
						continue

					elif next_piece == 'T':
						hints += 1
						actions.append((row - size + 1, col, size, 1, hints))
						return actions

					elif next_piece in ('M', 'U'):
						hints += 1
						continue

				return actions

			elif self.is_left_piece(piece):
				for size in self.get_available_sizes():  # This e excludes size 1

					if size == 1:
						continue

					next_piece = self.get_value(row, col + size - 1)

					if next_piece in ('w', 'W', None, 'L', 'T', 'B', 'C'):
						break

					elif self.is_empty(next_piece):
						actions.append((row, col, size, 0, hints))
						continue

					elif next_piece == 'R':
						hints += 1
						actions.append((row, col, size, 0, hints))
						return actions

					elif next_piece in ('M', 'U'):
						hints += 1
						continue

				return actions

			elif self.is_right_piece(piece):
				for size in self.get_available_sizes():  # This e excludes size 1

					if size == 1:
						continue

					next_piece = self.get_value(row, col - size + 1)

					if next_piece in ('w', 'W', None, 'R', 'T', 'B', 'C'):
						break

					elif self.is_empty(next_piece):
						actions.append((row, col - size + 1, size, 0, hints))
						continue

					elif next_piece == 'L':
						hints += 1
						actions.append((row, col - size + 1, size, 0, hints))
						return actions

					elif next_piece in ('M', 'U'):
						hints += 1
						continue

				return actions

			elif self.is_unknown_piece(piece):
				if self.is_u_single(row, col):
					actions.append((row, col, 1, 0, hints))
					return actions

			elif self.is_middle_piece(piece):
				pass

		return actions

	def get_guess_boats_row(self, row: int, size: int):

		actions = []
		hints = 0

		col = 0
		while col < 10:
			max_size = 0
			if self.is_empty(self.get_value(row, col)) or self.is_unknown_piece(self.get_value(row, col)):
				while self.is_empty(self.get_value(row, col + max_size)) or \
						self.is_unknown_piece(self.get_value(row, col + max_size)) or \
						self.is_middle_piece(self.get_value(row, col + max_size)):
					if self.is_unknown_piece(self.get_value(row, col + max_size)) or \
							self.is_middle_piece(self.get_value(row, col + max_size)):
						hints += 1

					max_size += 1

				if max_size >= size:
					for delta in range(0, max_size - size + 1):
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
				while self.is_empty(self.get_value(row + max_size, col)) or \
						self.is_unknown_piece(self.get_value(row + max_size, col)) or \
						self.is_middle_piece(self.get_value(row + max_size, col)):
					if self.is_unknown_piece(self.get_value(row + max_size, col)) or \
							self.is_middle_piece(self.get_value(row + max_size, col)):
						hints += 1

					max_size += 1

				if max_size >= size:
					for delta in range(0, max_size - size + 1):
						actions.append((row + delta, col, size, 1, hints))

			row += max_size + 1

		return actions

	def get_guess_based_actions(self):  # Retorna uma ou mais actions com um unico move

		if len(self.get_available_sizes()) == 0:
			return []

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


		for row in possible_rows:
			actions.extend(self.get_guess_boats_row(row, size))
		for col in possible_cols:
			actions.extend(self.get_guess_boats_col(col, size))

		return actions

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

		if not state.board.is_hints_empty():
			actions = state.board.get_hint_based_actions()  # Retorna uma unica action com 1 move
			if len(actions) > 0:
				return actions

		actions = state.board.get_guess_based_actions()  # Retorna varias actions com 1 move
		return actions

	def result(self, state: BimaruState, action):
		"""Retorna o estado resultante de executar a 'action' sobre
		'state' passado como argumento. A ação a executar deve ser uma
		das presentes na lista obtida pela execução de
		self.actions(state)."""

		new_board = state.board.copy_board()
		row, col, size, orientation, hints = action

		if new_board.place_boat(row, col, size, orientation, hints) or new_board.logic_away():
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
			if state.board.get_boats_left(size) != 0:
				return False

		# Verifica se todas as colunas e linhas estão cheias e com o número de peças de barco correto
		for coordenada in range(10):
			if (state.board.get_bpieces_left_row(coordenada) != '0') or \
					(state.board.get_bpieces_left_col(coordenada) != '0') or \
					(state.board.get_empty_spaces_row(coordenada) != '0') or \
					(state.board.get_empty_spaces_col(coordenada) != '0'):
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

	board = Board.parse_instance()
	problem = Bimaru(board)
	initial_state = BimaruState(board)
	goal_node = depth_first_tree_search(problem)



	print(goal_node.state.board, sep="")

"""
	import cProfile
	import pstats
	with cProfile.Profile() as pr:
		board = Board.parse_instance()
		problem = Bimaru(board)
		initial_state = BimaruState(board)
		goal_node = depth_first_tree_search(problem)

		print(goal_node.state.board, sep="")

	stats = pstats.Stats(pr)
	stats.sort_stats(pstats.SortKey.TIME)
	stats.print_stats()"""