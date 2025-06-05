program proquacks;
var n : int ;
  j , i : float;
  s : string;
 
void fact (n : int, a : float)
[  var b : float;
 
    if (n > 1 )
      {  b = a * n * 0.55;
         fact (n-1, b);  
      }
      else
      {  print(a);   }; 

];
 
 
void some_other( n : int )
[  var n : float
   { 
      n = "woooooooooo 9"; 
      print("hello "); 
      xf = 7;
 
      fact(3, 5.8);
   } 
];
 
 
main 
{  n = 5;
   fact(n, 1.1);
 
   fact(n+1, 1.2);
 
    do {
      print(3, "w", 4);
    }while( 3 <7 );
 
    if ( 3 >= 8)
    {
      print("texto ");
      n = 58 + 9 * 5;
    };
 
print("texto ");
some_other(4)
n = 58 + 9 * 5;
 
}
end;
