// Implements a dictionary's functionality

#include <stdbool.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
// [(26^3 + 26^2 + 26 + 1) * 26] = 475254 buckets for 
// first 4 letters of a word 
const unsigned int N = 475254;
#define BASE (71)

// Hash table
node *table[N];

// Numeber of words in the dictionary
unsigned int dic_length = 0;


// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    node *temp = table[hash(word)];
    
    // Look for word in the hash table
    while (temp != NULL)
    {
        if (!strcasecmp(temp->word, word))
        {
            return true;
        }
        temp = temp->next;
    }
    
    return false;
}


/** 
 * Hashes word to a number
 * 
 *  1. dictionary data types. C/HashTables. (n.d.). Retrieved September 24,
 *  2021, from https://www.cs.yale.edu/homes/aspnes/pinewiki/C(2f)HashTables.html?
 *  highlight=%28CategoryAlgorithmNotes%29. 
 * 
 *  Modified function to hash only first 4 lowercase letters of word
 *  Changed BASE to a prime number 
**/
unsigned int hash(const char *word)
{
    unsigned int h;
    unsigned const char *us;
   
    // cast s to unsigned const char 
    // this ensures that elements of s will be treated as having values >= 0 
    us = (unsigned const char *) word;
   
    h = 0;
    int count = 0;
    
    // Processes only first 4 letters
    while (count < 4) 
    {
        
        // Process words with less than 4 letters 
        if (*us == '\0')
        {
            break;
        }
        
        char c = tolower(*us);
    
        h = (h * BASE + c) % N;
        us++;
        count++;
    } 
  
    return h;
}

/** 
 * Loads dictionary into memory, returning true if successful, else false
**/
bool load(const char *dictionary)
{
    // Open dictionary file
    FILE *d_file = fopen(dictionary, "r");
    if (d_file == NULL)
    {
        return false;
    }
    
    char word[LENGTH + 1];
    int f_return = fscanf(d_file, "%s", word);
    
    // Add word from dictionary file to hash table
    // In the appropriate hashed position
    while (f_return != EOF)
    {
        // Create new node 
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            fclose(d_file);
            return false;
        }
        
        // Add word to node n
        strcpy(n->word, word);
        dic_length++;
        n->next = NULL;
        
        // Place word in hash table
        unsigned int t_num = hash(word);
        
        if (!(table[t_num] != NULL))
        {
            table[t_num] = n;
        }
        else
        {
            n->next = table[t_num];
            table[t_num] = n;
        }
        

        f_return = fscanf(d_file, "%s", word);
        if (ferror(d_file))
        {
            fclose(d_file);
            return false; 
        }
    }
    
    fclose(d_file);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    if (!dic_length)
    {
        return 0;
    }
    else
    {
        return dic_length;
    }
}

// Empties each node in a given linked list
void remove_Linkedlist(node *temp)
{
    if (temp == NULL)
    {
        return;
    }
    else
    {
        remove_Linkedlist(temp->next);
        free(temp);
    }
}


// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    for (int i = 0; i < N; i++)
    {
        if (table[i] != NULL)
        {
            remove_Linkedlist(table[i]);
        }
    }
    
    return true;
}