# Prints 2 half-pyramids using hashes (#) 
from cs50 import get_int


def main():
    
    h = 0
    # Get positive integer between 1 and 8, inclusive
    while(True):
        h = get_int("Height: ")
        if h > 0 and h < 9:
            break
        
    s = h
    # Print left and right aligned pyramid 
    for i in range(h):
        s -= 1
        print(" "*s+"#"*(h-s)+" "*2+"#"*(h-s))

        
if __name__ == "__main__":
    main() 