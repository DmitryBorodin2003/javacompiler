import os

import _parser
import semantic


def main():
    test = '''
    int factorial(int n) {
        if (n == 0 || n == 1) {
            return 1;
        } else {
            return n * factorial(n - 1);
        }
    }
    
    String hello = "Hello World!";
    int a = 4;
    int b = factorial(a);
    double pi = 3.14;
    if (a < b) {
        for (int i = 0; i < 10; i = i + 1) {
            a = a + i;
        }
    }
    else {
        b = 0.01;
    }
    '''

    execute(test)


def execute(prog: str):
    prog = _parser.parse(prog)
    print('ast:')
    print(*prog.tree, sep=os.linesep)

    print('semantic_check:')
    try:
        scope = semantic.prepare_global_scope()
        print("prepared")
        prog.semantic_check(scope)
        print(*prog.tree, sep=os.linesep)
    except semantic.SemanticException as e:
        print('Ошибка: {}'.format(e.message))
        return
    print()

if __name__ == "__main__":
    main()
