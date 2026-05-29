import csv
import os
from parser import FileBlock, BinaryBlock, WriteStatement, AppendStatement, ReadStatement, ReadLineStatement, ReadLinesStatement, WriteCsvStatement

class Interpreter:
    def execute(self, ast):
        # Executes each block in the Abstract Syntax Tree.
        for block in ast:
            if isinstance(block, FileBlock):
                self.execute_file_block(block)
            elif isinstance(block, BinaryBlock):
                self.execute_binary_block(block)

    def get_mode(self, statements, is_binary=False):
        """
        Determines the appropriate Python file mode based on the statements.
        'r' - read only
        'w' - write (truncates)
        'a' - append
        'r+' - read and write (no truncation)
        'a+' - read and append
        """
        has_read = any(isinstance(s, (ReadStatement, ReadLineStatement, ReadLinesStatement)) for s in statements)
        has_write = any(isinstance(s, WriteStatement) for s in statements)
        has_append = any(isinstance(s, AppendStatement) for s in statements)
        has_csv = any(isinstance(s, WriteCsvStatement) for s in statements)

        # Logic for mapping DSL behavior to Python modes
        if has_csv:
            # CSV handling is special
            return None

        mode = 'r'
        if has_write and not has_read:
            mode = 'w'
        elif has_append and not has_read:
            mode = 'a'
        elif has_read and has_write:
            mode = 'r+' # Read and write
        elif has_read and has_append:
            mode = 'a+' # Read and append
        elif has_read:
            mode = 'r'

        return mode + ('b' if is_binary else '')

    def execute_file_block(self, block):
        # Processes a text file block and its statements statefully.
        mode = self.get_mode(block.statements)

        try:
            # Special case: if mode is 'r+' but file doesn't exist, we will use 'w+' 
            if mode and ('r' in mode) and not os.path.exists(block.filename):
                if '+' in mode:
                    with open(block.filename, 'w') as f: pass

            if not mode: # Handle blocks with special operations like write_csv
                for stmt in block.statements:
                    if isinstance(stmt, WriteCsvStatement):
                        self.handle_csv_write(block.filename, stmt.source_file)
                return

            with open(block.filename, mode) as f:
                for stmt in block.statements:
                    if isinstance(stmt, WriteStatement):
                        f.write(stmt.content + '\n')
                    elif isinstance(stmt, AppendStatement):
                        f.write(stmt.content + '\n')
                    elif isinstance(stmt, ReadStatement):
                        print(f.read(), end='')
                    elif isinstance(stmt, ReadLineStatement):
                        print(f.readline(), end='')
                    elif isinstance(stmt, ReadLinesStatement):
                        print(f.readlines())
        except (IOError, OSError) as e:
            print(f"Tabulon Runtime Error: Could not process file '{block.filename}'. {e}")

    def execute_binary_block(self, block):
        """Processes a binary file block and its statements statefully."""
        mode = self.get_mode(block.statements, is_binary=True)

        try:
            if mode and ('r' in mode) and not os.path.exists(block.filename):
                if '+' in mode:
                    with open(block.filename, 'wb') as f: pass

            with open(block.filename, mode) as f:
                for stmt in block.statements:
                    if isinstance(stmt, WriteStatement):
                        f.write(stmt.content.encode('utf-8'))
                    elif isinstance(stmt, ReadStatement):
                        print(f.read())
                    elif isinstance(stmt, ReadLineStatement):
                        print(f.readline())
                    elif isinstance(stmt, ReadLinesStatement):
                        print(f.readlines())
        except (IOError, OSError) as e:
            print(f"Tabulon Runtime Error: Could not process binary file '{block.filename}'. {e}")

    def handle_csv_write(self, target_filename, source_filename):
        # Convert raw comma separated text to a formatted CSV
        try:
            with open(source_filename, 'r') as src, open(target_filename, 'w', newline='') as dest:
                writer = csv.writer(dest)
                for line in src:
                    row = line.strip().split(',')
                    if row:
                        writer.writerow(row)
        except (IOError, OSError) as e:
            print(f"Tabulon Runtime Error: CSV conversion failed. {e}")
