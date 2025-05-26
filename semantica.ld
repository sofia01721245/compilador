
program mayor_numero;

var x, y, z, mayor : int;

main {
    x = 10;
    y = 25;
    z = 15;

    if(x > y) {
        if (x > z) {
            mayor = x;
        } else {
            mayor = z;
        };
    } else {
        if (y > z) {
            mayor = y;
        } else {
            mayor = z;
        };
    };
    print(mayor);
}
end;
