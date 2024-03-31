import os

import _parser


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
    boolean c = False;
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


if __name__ == "__main__":
    main()
