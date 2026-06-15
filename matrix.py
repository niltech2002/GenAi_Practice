# Nested comprehension — flatten a 2D matrix
matrix   = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
flat     = [cell for row in matrix for cell in row]  
#  Read it like this: For each row in matrix, for each cell in that row, collect cell
print(f"Flattened: {flat}")