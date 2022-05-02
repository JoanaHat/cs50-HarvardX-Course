#include <stdio.h>
#include <cs50.h>

int main(void)
{
    //Get initial population
    int startP, endP;
    do
    {
        startP = get_int("Start size: ");  
    }
    while (startP < 9);
    
    //Get ending populattion 
    do
    {
        endP = get_int("End size: ");  
    }
    while (endP < startP);
    
    //Number of years to reach population
    int years = 0;
    int y = startP;
    
    while (y < endP)
    {
        y = y + (y / 3) - (y / 4);
        years++;
    }
    
    printf("Years: %i\n", years);
}