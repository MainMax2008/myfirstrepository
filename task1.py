print("Парсер арифметических выражений")
print("------------------------------------------")
print("Правила: напиши 0, если хочешь закончить/отрицательные числа пиши с пробелом, например, \n '(45+9)* -5' ")
print("Разрешены для написания цифры от 0 до 9, арифм. действия (+,-,*,/), скобки и пробелы")
print("------------------------------------------")
in_str = input("Введите выражение: ")
while in_str != "0":
    for c in in_str:
        if c not in '0123456789()/*-+ ':
            print('Ой-ой-ой, у тебя запрещенный символ в выражении! Напиши правильный вариант')
            in_str = input("Введите выражение: ")
            break
        else:
            if "++" in in_str or "--" in in_str or '**' in in_str or '//' in in_str:
                print("У тебя ошибка в выражении (лишний знак)! Напиши правильный вариант")
                in_str = input("Введите выражение: ")
            else:
                # in_str = in_str.replace('((','( (')
                # in_str = in_str.replace('))', ') )')
                # for c in '0123456789':
                #     in_str = in_str.replace(f'({c}', f'( {c}') \
                #         .replace(f'{c})', f'{c} )').replace(f' -{c}',f'&{c}')
                # for c in '+*/-':
                #     in_str = in_str.replace(c,f' {c} ')
                # for c in '0123456789':
                #     in_str = in_str.replace(f'&{c}', f'-{c}')
                for c in '0123456789':
                    in_str = in_str.replace(f' -{c}', f'~{c}')

                if in_str.startswith('-'):
                    in_str = '~' + in_str[1:]

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
    f = 0
    while len(massive)>1:
        if f==1: break
        for i in range(len(massive)):
            if massive[i]=='+' and massive[i-1] not in '()+/*-'  and massive[i-2] not in '()+/*-':
                massive = massive[:i-2] + [str(float(massive[i-2])+float(massive[i-1]))] + massive[i+1:]
                break
            elif massive[i]=='-' and massive[i-1] not in '()+/*-' and massive[i-2] not in '()+/*-':
                massive = massive[:i-2] + [str(float(massive[i-2])-float(massive[i-1]))] + massive[i+1:]
                break
            elif massive[i]=='*' and massive[i-1] not in '()+/*-' and massive[i-2] not in '()+/*-':
                massive = massive[:i-2] + [str(float(massive[i-2])*float(massive[i-1]))] + massive[i+1:]
                break
            elif massive[i]=='/':
                if float(massive[i - 1]) == 0:
                    print('Где-то происходит деление на 0. Так делать нельзя! Исправь')
                    f = 1
                    break
                else:
                    res = float(massive[i - 2]) / float(massive[i - 1])
                    massive = massive[:i - 2] + [str(res)] + massive[i + 1:]
                    break
    if f==0:
        print(f'Результат: {massive[0]}')
    in_str = input("Введите выражение: ")
print("Конец")
