#include <ctype.h>
#include <cs50.h>
#include <stdio.h>
#include <string.h>


int main(void)
{
    string text = get_string("Text: ");
    int letters = 0, words = 1, sentences = 0, grade = 0;
    float L = 0, S =  0, g = 0;
    
    // Counting number of words, letters and sentences submitted 
    for (int i = 0, n = strlen(text); i < n; i++)
    {
        char c = toupper(text[i]);
        // If char is a letter, increment letters 
        if (!(c < 'A' || c > 'Z'))
        {
            letters++;
        }
        
        // If char is space, increment words
        if (isspace(c))
        {
            words++;
        }
        
        // If char is sentence end punctuation, increment sentences
        if (c == '.' || c == '!' || c == '?')
        {
            sentences++;
        }
    }
     
    // Culculating L and S
    L = ((float)letters / words) * 100;
    S = ((float)sentences / words) * 100;
     
    // Coleman-Liau index formula
    g = 0.0588 * L - 0.296 * S - 15.8;
     
    // If g does not need to be rounded up, print trancated grade
    grade = g;
     
    // Get digit in the first decimal place
    // If digit is > or = to 5 round up grade
    g = (int)(g * 10) % 10;
    if (g >= 5)
    {
        grade++;
    }
     
    // Printing out grade reading level
    if (grade >= 16)
    {
        printf("Grade 16+\n");
    }
    else if (grade <= 0)
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %i\n", grade);
    }
}