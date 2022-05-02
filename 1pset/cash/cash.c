#include <stdio.h>
#include <cs50.h>
#include <math.h>


void tenCents(int count, int r);
void fiveCents(int count, int r);
void quarters(int count, int cents);


int main(void)
{
    //Get change amount  
    float change;
    do
    {
        change = get_float("Change owed: ");
    }
    while (change < 0);
    
    
     
    int cents = round(change * 100);
    int count = 0;
    
    //Calculate the number of change returned
    if (cents >= 25)
    {
        quarters(count, cents);
    }
    else if (cents >= 10)
    {
        tenCents(count, cents);
    }
    else if (cents >= 5)
    {
        fiveCents(count, cents);
    }
    else
    {
        printf("%i\n", cents);
    }
    
}

// Breaks down 25 cents and counts number of quarters
void quarters(int count, int cents)
{
    // This will track remainders
    int r = 0;
    // Counts how many quarters to return
    count = cents / 25; 
    //Testing to see if there is a remainder
    if (cents % 25) 
    {
        //Getting the remainder
        r = cents % 25; 
        if (r >= 10)
        {
            tenCents(count, r);
        }
        else if (r >= 5)
        {
            fiveCents(count, r);
        }
        else
        {
            count += r;
            printf("%i\n", count);
        }
    }
    else
    {
        printf("%i\n", count);
    }
}

// Breaks down 10 cents and counts number of dimes
void tenCents(int count, int r)
{
    // Adds to count the number of dimes to return
    count += (r / 10);
    if (r % 10)
    {
        r %= 10;
        if (r >= 5)
        {
            fiveCents(count, r);
        }
        else
        {
            count += r;
            printf("%i\n", count);
        }
    }
    else
    {
        printf("%i\n", count);
    }
}


// Breaks down 5 cents and counts number of nickels
void fiveCents(int count, int r)
{
    // Adds to count the number of nickels to return
    count += (r / 5);
    if (r % 5)
    {
        r %= 5;
        // Adds to count the number pennies to return
        count += r;
        printf("%i\n", count);
    }
    else
    {
        printf("%i\n", count);
    }
}