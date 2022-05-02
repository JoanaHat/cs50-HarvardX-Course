#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// Candidates have name and vote count
typedef struct
{
    string name;
    int votes;
}
candidate;

// Array of candidates
candidate candidates[MAX];

// Number of candidates
int candidate_count;

// Function prototypes
bool vote(string name);
void print_winner(void);

int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: plurality [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i].name = argv[i + 1];
        candidates[i].votes = 0;
    }

    int voter_count = get_int("Number of voters: ");

    // Loop over all voters
    for (int i = 0; i < voter_count; i++)
    {
        string name = get_string("Vote: ");

        // Check for invalid vote
        if (!vote(name))
        {
            printf("Invalid vote.\n");
        }
    }

    // Display winner of election
    print_winner();
}

// Update vote totals given a new vote
bool vote(string name)
{
    // Find voted name in array of candidates
    for (int i = 0; i < candidate_count; i++)
    {
        if (!strcmp(candidates[i].name, name))
        {
            candidates[i].votes += 1;
            return true;
        }
    }
    
    return false;
}

// Print the winner (or winners) of the election
void print_winner(void)
{
    // Order array from fewest votes to most votes 
    // Using selection sort algorithm
    for (int i = 0; i < candidate_count; i++)
    {
        int position = i;
        int smallest = candidates[i].votes;
        string name = candidates[i].name;
        
        // Find fewest votes of remaining array
        for (int j = i; j < candidate_count; j++)
        {
            if (candidates[j].votes < smallest)
            {
                smallest = candidates[j].votes;
                position = j;
                name = candidates[j].name;
            }
        }
        
        // Move fewest votes to the front of array
        candidates[position].votes =  candidates[i].votes;
        candidates[position].name =  candidates[i].name;
        candidates[i].votes = smallest;
        candidates[i].name = name;
    }
    
    // Print winners
    for (int i = 0; i < candidate_count; i++)
    {
        if (candidates[candidate_count - 1].votes == candidates[i].votes)
        {
            printf("%s\n", candidates[i].name);
        }
    }
 
    return;
}

