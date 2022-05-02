#include <stdio.h>
#include <cs50.h>

void space(int n);
void leftAlign(int temp);
void rightAlign(int h, int temp);

int main(void)
{
    // Get height of pyramids
    int h;
    do
    {
        h = get_int("Height: ");
    }
    while (h < 1 || h > 8);
    
    // Create pyramids
    int temp = 1;
    for (int i = 0; i < h; i++)
    {
        rightAlign(h, temp);
        space(2);
        leftAlign(temp);
        printf("\n");
        temp++; // controls how many # are being printed 
    }
    
}

//Prints n amount of spaces 
void space(int n)
{
    for (int i = 0; i < n ; i++)
    {
        printf(" ");
    }
}

//Aligns # rows to the right
void rightAlign(int h, int temp)
{
    for (int j = 0; j < temp; j++)
    {
        // temp is the number of # to be printed
        // to avoid printing spaces between #
        // print all spaces on the first iteration
        if (j == 0)
        {
            space((h - temp));
        }
        printf("#");
    }
}

//Aligns # rows to the left 
void leftAlign(int temp)
{
    for (int j = 0; j < temp; j++)
    {
        printf("#");
    }
}