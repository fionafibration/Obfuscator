# Python Obfuscator
## Use
Reads a python program from stdin, then compiles and serializes it using the marshal module. Then, encodes that serialization as a series of bitshifts and integers from 1-9, then puts these into a file with a Y combinator lambda to read the integers back as bytes, and obfuscated imports and calls to marshal.loads() and exec(). 
## Error Avoidance
Don't use any variable names that are only made up of underscores. That's about it.
## Example
Included is an example implementation of the SHA3 and Keccak hash functions, and the fully obfuscated version. Size of the file is increased monumentally, by nearly 60 times, and PyCharm crashes upon attempting to reformat the code. However, it works just as the unobfuscated version does, including identical variable names, classes, and all, even though there is a noticeable delay upon importing the file.
