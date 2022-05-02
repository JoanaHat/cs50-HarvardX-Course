#include <ctype.h>
#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


int main(int argc, string argv[])
{
    if (argc == 2)
    {
        // Check if key is a decimal number
        for (int i = 0, n = strlen(argv[1]); i < n; i++)
        {
            // if a non-negative nuber is found return error message
            if (!(isdigit(argv[1][i])))
            {
                printf("Usage: ./caesar key\n");
                return 1;
            }
        }
        
        string pText = get_string("plaintext: ");
        int len = strlen(pText);
        char cText[len];
        int key = atoi(argv[1]);
        key = key % 26;
        
        // If key is a multiple of 26 or 0 return plaintext
        if (key == 0)
        {
            printf("ciphertext: %s\n", pText);
            return 0;
        }
        
        // Cipher plaintext to ciphertext
        for (int i = 0; i < len; i++)
        {
            char c = toupper(pText[i]);
            
            if (!(c < 'A' || c > 'Z'))
            {
                c = pText[i] + key;
                
                // Adding the key to some lowercase letters can yield a negative number
                // Converting the letter into an integer first, mitigates this
                int letter = pText[i];
                int sum = letter + key;
                
                // Wraps around uppercase alphabet once 'Z' is reached
                if (c > 'Z' && isupper(pText[i]))
                {
                    int n = c - 'Z';
                    c = 65 + (n - 1);
                }
                
                // Wraps around lowercase alphabet once 'z' is reached
                if (sum > 'z')
                {
                    int n = sum - 'z';
                    c = 97 + (n - 1);
                }
                
                // Adds ciphered letter to ciphertext
                cText[i] = c;
            }
            else
            {
                cText[i] = pText[i];
            }
        }
        
        // Print ciphertext
        cText[len] = '\0';
        printf("ciphertext: %s", cText);
        printf("\n");
        return 0;
    }
    else
    {
        printf("Usage: ./caesar key\n");
        return 1;
    }
}