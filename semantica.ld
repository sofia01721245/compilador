
program complete_test;
var counter : int;
var result : float;
var message : string;

void math_operations(a : int, b : float, c : int)
[ var temp : int;
  var factor : float;
  var output : string;
  { 
    temp = a * c;
    factor = b + temp;
    output = "Result: ";
    
    if(factor > 10.0)
    {
      print(output);
      print(factor);
    }
    else
    {
      temp = temp - 5;
      print(temp);
    };
  }
];

void string_processor(text : string, length : int)
[ var processed : string;
  var count : int;
  {
    processed = text;
    count = length;
    
    print("Processing: ");
    print(processed);
    print("Length: ");
    print(count);
  }
];

main 
{
  counter = 0;
  result = 0.0;
  message = "Hello World";
  
  math_operations(5, 3.14, 2);
  math_operations(1, 15.5, 3);

  
  string_processor("Test String", 11);
  string_processor(message, 11);
  
  counter = 1;
  do {
    result = result + counter * 2.5;
    counter = counter + 1;
    print("Iteration: ");
    print(counter);
    print("Result: ");
    print(result);
  } while(counter <= 5);
  
  counter = 10 + 5 * 3;
  result = counter / 2.0;
  
  print("Final counter: ");
  print(counter);
  print("Final result: ");
  print(result);
}
end;
