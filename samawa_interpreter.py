import re
import sys

class SamawaInterpreter:
    def __init__(self):
        self.vars = {}
        self.functions = {}

    def tokenize(self, code):
        token_spec = [
            ('VAR', r'var\b'),
            ('FUNGSI', r'fungsi\b'),
            ('lamen', r'lamen\b'),
            ('ulang dean', r'ulang dean\b'),
            ('kaleng', r'kaleng\b'),
            ('KE', r'ke\b'),
            ('semalik dean', r'semalik\b'),
            ('NUMBER', r'\d+'),
            ('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('STRING', r'"[^"]*"'),
            ('OPERATOR', r'[+\-*/=<>!]+'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('SEMICOLON', r';'),
            ('COMMENT', r'//.*'),
            ('WHITESPACE', r'\s+'),
        ]
        
        tokens = []
        pos = 0
        while pos < len(code):
            match = None
            for token_type, pattern in token_spec:
                regex = re.compile(pattern)
                match = regex.match(code, pos)
                if match:
                    value = match.group(0)
                    if token_type not in ('WHITESPACE', 'COMMENT'):
                        tokens.append((token_type, value))
                    pos = match.end()
                    break
            if not match:
                raise SyntaxError(f"Token tidak valid di posisi {pos}: {code[pos:pos+20]}")
        return tokens

    def parse(self, tokens):
        ast = []
        i = 0
        while i < len(tokens):
            token_type, token_value = tokens[i]
            
            if token_type == 'VAR' and i+3 < len(tokens):
                # Format: var x = value;
                var_name = tokens[i+1][1]
                if tokens[i+2][1] == '=':
                    var_value = tokens[i+3][1]
                    ast.append(('VAR_DECLARE', var_name, var_value))
                    i += 4
                else:
                    raise SyntaxError("Format deklarasi var salah")
            
            elif token_type == 'JIKA' and i+4 < len(tokens):
                # Format: jika (condition) { ... }
                if tokens[i+1][1] == '(' and tokens[i+3][1] == ')':
                    condition = tokens[i+2][1]
                    if tokens[i+4][1] == '{':
                        block = []
                        brace_count = 1
                        i += 5
                        while i < len(tokens) and brace_count > 0:
                            if tokens[i][1] == '{':
                                brace_count += 1
                            elif tokens[i][1] == '}':
                                brace_count -= 1
                            if brace_count > 0:
                                block.append(tokens[i])
                            i += 1
                        ast.append(('IF', condition, block))
                    else:
                        raise SyntaxError("Tidak ada pembuka blok { setelah jika")
                else:
                    raise SyntaxError("Format kondisi jika salah")
            
            elif token_type == 'ULANGI' and i+8 < len(tokens):
                # Format: ulangi (i dari 1 ke 10) { ... }
                if (tokens[i+1][1] == '(' and tokens[i+3][1] == 'dari' and 
                    tokens[i+5][1] == 'ke' and tokens[i+7][1] == ')'):
                    loop_var = tokens[i+2][1]
                    start = tokens[i+4][1]
                    end = tokens[i+6][1]
                    if tokens[i+8][1] == '{':
                        block = []
                        brace_count = 1
                        i += 9
                        while i < len(tokens) and brace_count > 0:
                            if tokens[i][1] == '{':
                                brace_count += 1
                            elif tokens[i][1] == '}':
                                brace_count -= 1
                            if brace_count > 0:
                                block.append(tokens[i])
                            i += 1
                        ast.append(('LOOP', loop_var, start, end, block))
                    else:
                        raise SyntaxError("Tidak ada pembuka blok { setelah ulangi")
                else:
                    raise SyntaxError("Format perulangan ulangi salah")
            else:
                i += 1
        return ast

    def execute(self, ast):
        for node in ast:
            if node[0] == 'VAR_DECLARE':
                var_name, var_value = node[1], node[2]
                self.vars[var_name] = self.evaluate_expression(var_value)
                print(f"[VAR] {var_name} = {self.vars[var_name]}")
            
            elif node[0] == 'IF':
                condition, block = node[1], node[2]
                if self.evaluate_condition(condition):
                    print("[IF] Kondisi benar, menjalankan blok")
                    block_ast = self.parse(block)
                    self.execute(block_ast)
            
            elif node[0] == 'LOOP':
                loop_var, start, end, block = node[1], node[2], node[3], node[4]
                start_val = int(self.evaluate_expression(start))
                end_val = int(self.evaluate_expression(end))
                print(f"[LOOP] Mengulang {loop_var} dari {start_val} ke {end_val}")
                
                for i in range(start_val, end_val + 1):
                    self.vars[loop_var] = i
                    block_ast = self.parse(block)
                    self.execute(block_ast)

    def evaluate_expression(self, expr):
        try:
            # Evaluasi ekspresi sederhana
            if expr.isdigit():
                return int(expr)
            elif expr in self.vars:
                return self.vars[expr]
            elif expr.startswith('"') and expr.endswith('"'):
                return expr[1:-1]
            else:
                return expr
        except:
            return expr

    def evaluate_condition(self, cond):
        # Evaluasi kondisi sederhana
        if '>' in cond:
            parts = cond.split('>')
            left = self.evaluate_expression(parts[0].strip())
            right = self.evaluate_expression(parts[1].strip())
            return float(left) > float(right)
        # Tambahkan operator lain sesuai kebutuhan
        return False

def main():
    if len(sys.argv) != 2:
        print("Penggunaan: python samawa_interpreter.py <file.samawa>")
        return
    
    filename = sys.argv[1]
    if not filename.endswith('.samawa'):
        print("Error: File harus berekstensi .samawa")
        return
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        
        interpreter = SamawaInterpreter()
        tokens = interpreter.tokenize(code)
        ast = interpreter.parse(tokens)
        interpreter.execute(ast)
    
    except FileNotFoundError:
        print(f"Error: File {filename} tidak ditemukan")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()