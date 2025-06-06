
program prockaks;
var n : int;

void fact(n:int, a:int)
[ var b: int;
    { if(n>1)
        {
            b=a*n;
            fact(n-1, b);
        }else
        { print(a); };
    }
];

main
{   
n = 5;
    fact(n, 1);
    fact(n+1, 1);
}
end;
