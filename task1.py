print("Парсер арифметических выражений")
print("------------------------------------------")
print("Правила: напиши 0, если хочешь закончить/отрицательные числа пиши с пробелом, например, \n '(45+9)* -5' ")
print("Разрешены для написания цифры от 0 до 9, арифм. действия (+,-,*,/), скобки и пробелы")
print("------------------------------------------")

while True:
    in_str = input("Введите выражение: ")

    if in_str.strip() == "0":
        print("Конец")
        break

    if not in_str.strip():
        print("Вы ничего не ввели! Напиши правильный вариант")
        continue
    z = False
    for c in in_str:
        if c not in '0123456789()/*-+. ':
            print('Ой-ой-ой, у тебя запрещенный символ в выражении! Напиши правильный вариант')
            z = True
            break
    if z:
        continue

    in_cstr = in_str.replace(' ', '')
    if "++" in in_cstr or "--" in in_cstr or '**' in in_cstr or '//' in in_cstr or '+*' in in_cstr \
            or '+-' in in_cstr or '+/' in in_cstr or '-+' in in_cstr or '-/' in in_cstr or \
            '-*' in in_cstr or '/+' in in_cstr or '/-' in in_cstr or '/*' in in_cstr \
            or '*+' in in_cstr or '*-' in in_cstr or '*/' in in_cstr:
        print("У тебя ошибка в выражении (лишний знак)! Напиши правильный вариант")
        continue
    elif in_cstr=='()' or in_cstr in \
            ['+','-','/','*','(',')']:
        print("У тебя ошибка в выражении (лишь один знак или скобки)! Напиши правильный вариант")
        continue
    elif in_str.count('(') != in_str.count(')'):
        print("У тебя ошибка в выражении (не хватает скобок)! Напиши правильный вариант")
        continue

    for c in '0123456789':
        in_str = in_str.replace(f' -{c}', f'~{c}')

    if in_str.startswith('-'):
        in_str = '~' + in_str[1:]
    for op in '(/*+-':
        in_str = in_str.replace(op + '-', op + '~')

    for c in '()+-*/':
        in_str = in_str.replace(c, f' {c} ')

    in_str = in_str.replace('~ ', '-').replace('~', '-')
    token_str = in_str.split()
    massive = []
    stack = []
    for c in token_str:
        if c not in '()+/*-':
            massive.append(c)
        else:
            if c == '+' or c=='-':
                while len(stack)>0 and stack[-1] in '/*+-':
                    massive.append(stack[-1])
                    stack.pop()
                stack.append(c)
            if c == '*' or c=='/':
                while len(stack)>0 and stack[-1] in '/*':
                    massive.append(stack[-1])
                    stack.pop()
                stack.append(c)
            if c=='(':
                stack.append(c)
            if c==')':
                while stack[-1] != '(':
                    massive.append(stack[-1])
                    stack.pop()
                stack.pop()
    if len(stack)!=0:
        stack = stack[::-1]
        for c in stack:
            massive.append(c)
        stack = []

    str_eval = []
    error = 0

    for token in massive:
        if token not in ['+', '-', '*', '/']:
            try:
                str_eval.append(float(token))
            except ValueError:
                print(f"Ошибка: некорректное число '{token}'.")
                error = 1
                break
        else:
            if len(str_eval) < 2:
                print("У тебя ошибка в выражении (лишние знаки или не хватает чисел)! Напиши правильный вариант")
                error = 1
                break
            b = str_eval.pop()
            a = str_eval.pop()
            if token == '+':
                str_eval.append(a + b)
            elif token == '-':
                str_eval.append(a - b)
            elif token == '*':
                str_eval.append(a * b)
            elif token == '/':
                if b == 0:
                    print('Где-то происходит деление на 0. Так делать нельзя! Исправь')
                    error = 1
                    break
                str_eval.append(a / b)

    if not error:
        if len(str_eval) == 1:
            print(f'Результат: {str_eval[0]}')
        elif len(str_eval) > 1:
            print("У тебя ошибка в выражении (пропущены арифметические знаки)! Напиши правильный вариант")
