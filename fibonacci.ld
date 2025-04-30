
#Programa caso de prueba fibonacci hasta n

program fibonacci;
var
    n, i, a, b, temp : int;

main{
	a = 0;
	b = 1;
	n = 10;
	i = 0;
	do {
        	print(a);
        	temp = b;
        	b = a + b;
        	a = temp;
        	i = i + 1;
	} while(i < n);
}
end
