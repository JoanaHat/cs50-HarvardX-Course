#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <regex.h> 
#include <string.h>

 
typedef uint8_t  BYTE;

typedef struct
{
    BYTE  b1;
    BYTE  b2;
    BYTE  b3;
    BYTE  b4;
} __attribute__((__packed__))
SIGNATURE;


int main(int argc, char *argv[])
{
    //Ensure proper usage 
    if (argc != 2)
    {
        printf("Usage: recover image\n");
        return 1;
    }
    
    // Open image file
    FILE *img_raw = fopen(argv[1], "r");
    if (!img_raw)
    {
        printf("Error in opening %s!\n", argv[1]);
        return 2;  
    }
    
    // Buffer to verify jpeg signature
    SIGNATURE bf;
    
    // Regular expression to compare the forth byte of signature 
    regex_t rx;
    int r = regcomp(&rx, "[eE][0-9a-fA-F]", 0);
    
    // Terminate if regular expression failed to compile
    if (r)
    {
        printf("Error creating rx!!\n");
    }
    
    BYTE *bf2 = malloc(508 * sizeof(BYTE) + 1);
    char *s_b4 = malloc(8 * sizeof(BYTE) + 1); 
    
    // Search for beginning of first image
    do 
    {
        fread(&bf, sizeof(SIGNATURE), 1, img_raw);
        sprintf(s_b4, " %x", bf.b4);
    }
    while (bf.b1 != 0xff || bf.b2 != 0xd8 || bf.b3 != 0xff || regexec(&rx, s_b4, 0, NULL, 0));
    
    
    int count = 0;
    int end = 0;
    char name[8];
   
    // Place each image in a file 
    while (!feof(img_raw))
    { 
        // Create new image file name with format ###.jpg
        sprintf(name, "%.3d.jpg", count);
        
        // Open new image file
        FILE *img = fopen(name, "w");
        if (!img) 
        {
            printf("Error in opening file %s!\n", name);
            return 2;
        }
        
        // Extract one picture 
        do 
        {
            fwrite(&bf, sizeof(SIGNATURE), 1, img);
            fread(bf2, sizeof(BYTE), 508, img_raw);
            fwrite(bf2, sizeof(BYTE), 508, img);
            end = fread(&bf, sizeof(SIGNATURE), 1, img_raw);
            sprintf(s_b4, " %x", bf.b4);
            
            if (!end)
            {
                break;
            }
        }
        while (bf.b1 != 0xff || bf.b2 != 0xd8 || bf.b3 != 0xff || regexec(&rx, s_b4, 0, NULL, 0));
        
        // Close completed image file
        fclose(img);
        count++;
    }
    
    // Clean up
    free(bf2);
    free(s_b4);
    regfree(&rx);
    fclose(img_raw);
    return 0;
}
