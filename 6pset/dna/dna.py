# Identifies the match of a given sequence of DNA
import csv
import sys


def main():
    # Ensure correct usage
    if len(sys.argv) != 3:
        sys.exit("Usage: python dna.py databases sequences")

    # Read dna sequence into memory
    sequence = ""
    with open(sys.argv[2], "r") as file:
        reader = csv.reader(file)
        for row in reader:
            sequence = str(row)

    dataBase = []
    # Read database into memory
    with open(sys.argv[1], "r") as file:
        reader = csv.reader(file)
        for row in reader:
            dataBase.append(row)

    def repeat(sequence, STR, p):
        '''Finds occurrences of a given STR in a sequence'''
        count = 0
        str_len = len(STR)

        # Find first occurence
        p = sequence.find(STR, p)

        # Base case
        if p == -1:
            return
        else:
            # Counts consecutive repeats of an STR in a sequence
            while True:
                count += 1
                p_next = p + str_len
                p = sequence.find(STR, p_next)
                if p != p_next:
                    break
            # Store consecutive repeats
            repetition.append(count)
            return repeat(sequence, STR, p)

    # List of STRs
    s = dataBase[0][1:]
    dna = []
    # Search for occurence of all  STRs in the dna sequence
    for STR in s:
        repetition = []
        repeat(sequence, STR, 0)
        if repetition:
            str_max = max(repetition)
            dna.append(str(str_max))

    # Search for dna sequence match in the database
    # Print match
    for d in dataBase:
        if d[1:] == dna:
            sys.exit(d[0])

    sys.exit("No match")


if __name__ == "__main__":
    main()