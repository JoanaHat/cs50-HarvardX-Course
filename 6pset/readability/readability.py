# Computes approximate grade level required to 
# comprehend a given text using Coleman-Liau index
from cs50 import get_string
import string


def main():
    # Get text
    text = get_string("Text: ")
    # Get number of words
    words = len(text.split())
    alphbt = string.ascii_letters
    
    # Count number of letters and sentences in text
    letters = 0
    sentences = 0
    for i in text:
        if i in alphbt:
            letters += 1
        elif i in ['.', '!', '?']:
            sentences += 1
    
    # Culculating L and S
    L = (letters / words) * 100
    S = (sentences / words) * 100
    
    # Coleman-Liau index formula
    g = round(0.0588 * L - 0.296 * S - 15.8)
    
    # Print out grade
    if g >= 16:
        print("Grade 16+")
    elif g <= 0:
        print("Before Grade 1")
    else:
        print("Grade " + str(g))
    
    
if __name__ == "__main__":
    main()    