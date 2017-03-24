# Python Obfuscator
## Use
Simply pass it an input file with a complete python program, and it will obfuscate it. It compresses using ZLIB, and encodes it with base64, then as a single, base256 number, then as a block of addition, subtraction, and bit shifts using only the numerals 1-8, represented by the variables with names made of 2-9 underscores. For example, 1 is "\_\_" and 8 is "________\_". This entire block of operations is calculated for any given number using the recursive algorithm over [here](https://benkurtovic.com/2014/06/01/obfuscating-hello-world.html)
## Error Avoidance
Don't use any variable names that are only made up of underscores. That's about it.
