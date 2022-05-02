# Checks validity of a credit card according to Luhn’s algorithm
from cs50 import get_int
import sys


def main():
    while True:
        # Get credit card number
        creditCard = get_int("Number: ")
        
        # Analyze user input number
        if creditCard > 0:
            total = 0
            card_num = str(creditCard)
            l = len(card_num)
            
            # Curate desired creditcard number length
            if l not in [13, 15, 16]:
                print("INVALID")
                sys.exit(0) 
            
            # Reverse card number
            rev_Cardnum = card_num[::-1]
            
            # Luhn’s Algorithm calculation   
            for n in rev_Cardnum[0::2]:
                total += int(n)
            
            # Calculating from second last number
            for c in rev_Cardnum[1::2]:
                x = str(int(c) * 2)
                
                if x[0] == '1':
                    total += (1 + int(x[1]))
                else:
                    total += int(x)
            
            # Validate credit card number
            if total % 10 != 0:         
                print("INVALID") 
                sys.exit(0)
        
            # Print card type    
            if int(card_num[:2]) in [51, 52, 53, 54, 55] and l == 16:
                print("MASTERCARD")
            elif int(card_num[:2]) in [34, 37] and l == 15:
                print("AMEX")
            elif int(card_num[:1]) == 4 and l in [13, 16]:
                print("VISA") 
                
            sys.exit(0)
        
        
if __name__ == "__main__":
    main()    