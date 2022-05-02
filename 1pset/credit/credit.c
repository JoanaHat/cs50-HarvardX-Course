#include <stdio.h>
#include <cs50.h>



int main(void)
{
    // Get credit card number
    long creditNum;
    do
    {
        creditNum = get_long("Number: ");
    }
    while (creditNum < 0);
    
    
    int c = 0; 
    int even = 0; 
    int odd = 0;
    int sum = 0;
    long number = creditNum;
    
    // First step of Luhn's Algorithm
    while (creditNum)
    {
        int n = 0; 
        int r = 0;
        c++;
        
        // Gets last digit of creditNum
        n = creditNum % 10;  
        
        // Selects every other digit starting with 
        // the second-to-last-digit
        if (!(c % 2)) 
        {
            n *= 2;
            if (n >= 10)
            {
                // Adds each digit of n to the overall sum
                even += 1; 
                r = n % 10;
                even += r;
            }
            else
            {
                even += n;
            }
        }
        else
        {
            odd += n;
        }
        
        // removes the last digit from creditNum
        creditNum /= 10; 
    }
    
    // Second step of Luhn's Algorithm 
    sum = odd + even;
    
    // Third step of Luhn's Algorithm (validating)
    if (!(sum % 10))
    {
        int count = 0;
        bool MASTERCARD = false;
        bool AMEX = false;
        int n;
        
        while (number)
        {
            count++;
            n = number % 10;
            number /= 10;
            
            // Checks for the 2nd digit of 
            // Mastercard and AMEX 
            if (count == (c - 1))
            {
                // If 2nd digit is present set card to true
                switch (n)
                {
                    case 1 :
                        MASTERCARD = true;
                        break;
                    case 2 :
                        MASTERCARD = true;
                        break;
                    case 3 :
                        MASTERCARD = true;
                        break;
                    case 4 :
                        MASTERCARD = true;
                        AMEX = true;
                        break;
                    case 5 :
                        MASTERCARD = true;
                        break;
                    case 7 :
                        AMEX = true;
                        break;
                }
            }
            
            // Checks the first digit n of the card number accordingly  
            // Checks for the length of the card number accordingly
            if (count == c)
            {
                switch (n)
                {
                    case 3 : 
                        if (AMEX && (c == 15))
                        {
                            printf("AMEX\n");
                        }
                        else
                        {
                            printf("INVALID\n");
                        }
                        break;
                    case 4 :
                        if (c == 13 || c == 16)
                        {
                            printf("VISA\n");
                        }
                        else
                        {
                            printf("INVALID\n");
                        }
                        break;
                    case 5 :
                        if (MASTERCARD && (c == 16))
                        {
                            printf("MASTERCARD\n");
                        }
                        else
                        {
                            printf("INVALID\n");
                        }
                        break;
                    default :
                        printf("INVALID\n");    
                }
            }
        }
    }
    else
    {
        printf("INVALID\n");
    }
}
