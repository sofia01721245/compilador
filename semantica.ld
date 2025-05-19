
program prueba3;

var A, B : int;

main {
    A = 3;
    B = 5;

    do {
        A = A + 1;
        B = B - 1;
    } while (A < B);

    do {
        A = A + 1;
    } while (A + B);
} end;

