#include <ctype.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>


int rep_Letters(char key[]);
int cipher(char key[]);


int main(int argc, string argv[])
{
    // Chack for required number of arguments
    if (argc == 2)
    {
        // Check for valid key length
        if (strlen(argv[1]) == 26)
        {
            char key[27];
            
            // Checking for letters that are not an alphabetic character
            for (int i = 0; i < 26; i++)
            {
                key[i] = toupper(argv[1][i]);
                if (!(isalpha(argv[1][i])))
                {
                    printf("Key must only contain letters.\n");
                    return 1;
                }
            }
            
            // End char array with NULL to avoid random memory access
            key[26] = '\0';
            
            // Check for repetition
            if (rep_Letters(key))
            {
                printf("Key must not contain repeated letters.\n");
                return 1;
            }
            
            // Cipher plaintext to ciphertext
            if (!cipher(key))
            {
                return 0;
            }
            
        }
        else
        {
            // Print error is key has less than or more than 26 characters
            printf("Key must contain 26 characters.\n");
            return 1;
        }
    }
    else
    {
        // Print error if arguments are more than 2 
        printf("Usage: ./substitution key\n");
        return 1;
    }
}

// This function checks for letter repetition in the Key
int rep_Letters(char key[])
{
    for (int i = 0; i < 26; i++)
    {
        for (int j = i + 1; j < 26; j++)
        {
            if (key[i] == key[j])
            {
                return 1;
            }
        }
    }
    
    return 0;
}

// Cipher plaintext to ciphertext
int cipher(char key[])
{
    // Get user's plaintext 
    string plaintext = get_string("plaintext: ");
    int len = strlen(plaintext);
    char ciphertext[len];
    string sub_plain = plaintext;
    
    // Ciper each character in plaintext
    for (int i = 0; i < len; i++)
    {
        // Simplifies verification of both uppercase and lowercase letters 
        char c = toupper(sub_plain[i]);
        
        // Check if plaintext character is an alphabetic character
        if (!(c < 'A' || c > 'Z'))
        {
            int count = 0;
            
            // Find position of plaintext character in the alphabet and get Key
            for (int j = 'A'; j <= 'Z'; j++)
            {
                if (c == j)
                {
                    if (islower(plaintext[i]))
                    {
                        // Capitalize key accordingly 
                        ciphertext[i] = tolower(key[count]);
                        break;
                    }
                    else
                    {
                        ciphertext[i] = toupper(key[count]);
                        break;
                    }
                }
                count++; 
            }
        }
        else
        {
            ciphertext[i] = plaintext[i];
        }
    }
    ciphertext[len] = '\0';
    printf("ciphertext: %s", ciphertext);
    printf("\n");
    return 0; 
}
