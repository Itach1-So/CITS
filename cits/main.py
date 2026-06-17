#!/usr/bin/env python3
"""
CITS - Main entry point
"""

import sys
import os
from .lexer import CitsLexer
from .parser import CitsParser
from .interpreter import CitsInterpreter
from .ast import *

def run_file(filename: str):
    """Execute a CITS program file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except FileNotFoundError:
        print(f"[!] File '{filename}' not found")
        return
    
    try:
        # Change to file's directory for relative paths
        file_dir = os.path.dirname(os.path.abspath(filename))
        if file_dir:
            os.chdir(file_dir)
        
        # Lex
        lexer = CitsLexer()
        tokens = lexer.tokenize(code)
        
        # Parse
        parser = CitsParser(tokens)
        statements = parser.parse_program()
        
        # Create interpreter and run
        interpreter = CitsInterpreter()
        
        # Add statements to program with line numbers
        line_num = 10
        for stmt in statements:
            interpreter.add_line(line_num, stmt)
            line_num += 10
        
        print(f"\n[*] Running '{os.path.basename(filename)}'...\n")
        interpreter.run()
        
    except SyntaxError as e:
        print(f"[!] Syntax error: {e}")
    except RuntimeError as e:
        print(f"[!] Runtime error: {e}")
    except Exception as e:
        print(f"[!] Error: {e}")

def interactive_mode():
    """Interactive REPL mode"""
    print("\n" + "="*50)
    print("[*] CITS Programming Language v1.0")
    print("[*] A Basic language by ITACHI")
    print("[*] ===============================")
    print("[*] Commands:")
    print("[*]   RUN                 - Execute program")
    print("[*]   LIST                - Show program")
    print("[*]   NEW                 - Clear program")
    print("[*]   DEL line_number     - Delete a line")
    print("[*]   exit                - Exit")
    print("[*]")
    print("[*] ===============================")
    
    interpreter = CitsInterpreter()
    
    while True:
        try:
            line = input(">>> ").strip()
            if not line:
                continue
            
            if line.lower() == 'exit':
                print("[*] Goodbye!")
                break
            elif line.upper() == 'RUN':
                interpreter.run()
            elif line.upper() == 'LIST':
                interpreter.list_program()
            elif line.upper() == 'NEW':
                interpreter.clear()
                print("[*] Program cleared")
            elif line.upper().startswith('DEL '):
                try:
                    line_num = int(line[4:])
                    interpreter.delete_line(line_num)
                    print(f"[*] Line {line_num} deleted")
                except:
                    print("[!] Usage: DEL line_number")
            elif line[0].isdigit():
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    try:
                        line_num = int(parts[0])
                        code = parts[1]
                        
                        lexer = CitsLexer()
                        tokens = lexer.tokenize(code)
                        parser = CitsParser(tokens)
                        stmt = parser.parse_statement()
                        
                        if stmt:
                            interpreter.add_line(line_num, stmt)
                            print(f"[*] Line {line_num} added")
                    except ValueError:
                        print("[!] Invalid line number")
                    except Exception as e:
                        print(f"[!] Error: {e}")
                else:
                    print("[!] Invalid format")
            else:
                print("[!] Unknown command")
                
        except KeyboardInterrupt:
            print("\n[*] Goodbye!")
            break
        except Exception as e:
            print(f"[!] Error: {e}")

def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        interactive_mode()
    elif len(sys.argv) == 2:
        filename = sys.argv[1]
        if filename.endswith('.cits'):
            run_file(filename)
        else:
            print("[!] Please specify a .cits file")
    else:
        print("Usage: cits [filename.cits]")

if __name__ == "__main__":
    main()