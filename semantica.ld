program prueba_semantica;

var A, B, C : int;
var D, E : float;

main {
    A = 10;
    B = 2;
    C = A + B * 3;  
    D = 4.5;
    E = D / 2.0;    

    A = 5.6;

    X = 2;

    if (A > B) {
        C = C - 1;
    };

    if (A + B) {
        C = A;
    };

    if (A < B) {
        A = A + 1;
    } else {
        B = B - 1;
    };

    do {
        A = A - 1;
    } while (A > 0);
} end;
