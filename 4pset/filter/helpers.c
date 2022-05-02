#include <stdio.h>
#include <cs50.h>
#include <stdlib.h>
#include "helpers.h"


int round_up(float n);
void capped(int *num);
// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Calculating average 
            float temp = ((float)image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3;
            int g_scale = round_up(temp);

            image[i][j].rgbtBlue = g_scale;
            image[i][j].rgbtGreen = g_scale;
            image[i][j].rgbtRed = g_scale;
        }
    }
    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            //printf("r:%i g:%i b:%i", image[i][j].rgbtRed, image[i][j].rgbtGreen, image[i][j].rgbtBlue);
            // modifying the third byte to sepia Red
            float sepiaRed = (float).393 * image[i][j].rgbtRed + .769 * image[i][j].rgbtGreen + .189 * image[i][j].rgbtBlue;
            int s_R = round_up(sepiaRed);
            capped(&s_R);

            // modifying the second byte to sepia Green
            float sepiaGreen = (float).349 * image[i][j].rgbtRed + .686 * image[i][j].rgbtGreen + .168 * image[i][j].rgbtBlue;
            int s_G = round_up(sepiaGreen);
            capped(&s_G);
            
            // modifying the first byte to sepia blue
            float sepiaBlue = (float).272 * image[i][j].rgbtRed + .534 * image[i][j].rgbtGreen + .131 * image[i][j].rgbtBlue;
            int s_B = round_up(sepiaBlue);
            capped(&s_B);
            
            
            image[i][j].rgbtRed = s_R;
            image[i][j].rgbtGreen = s_G;
            image[i][j].rgbtBlue = s_B;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        int sub = 1;
        for (int j = 0; j < width / 2; j++)
        {
            // Swap pixels from the right of image to the left
            RGBTRIPLE temp = image[i][j];
            image[i][j] = image[i][width - sub];
            image[i][width - sub] = temp;
            sub++;
        }
    }

    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // Copy array of pixel
    RGBTRIPLE(*copy)[width] = calloc(height, width * sizeof(RGBTRIPLE));
    //if (!copy)
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            copy[i][j] = image[i][j];
        }
    }
    
    // Adding all the values of each pixel
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int count = 0;
            bool j_min = false;
            bool j_add = false;

            int r_blue = copy[i][j].rgbtBlue;
            int r_green = copy[i][j].rgbtGreen;
            int r_red = copy[i][j].rgbtRed;
            count++;

            // pixels on left 
            if ((j - 1) >= 0)
            {
                r_blue += copy[i][j - 1].rgbtBlue;
                r_green += copy[i][j - 1].rgbtGreen;
                r_red += copy[i][j - 1].rgbtRed;
                j_min = true;
                count++;
            }

            // Pixel on right
            if ((j + 1) < width)
            {
                r_blue += copy[i][j + 1].rgbtBlue;
                r_green += copy[i][j + 1].rgbtGreen;
                r_red += copy[i][j + 1].rgbtRed;
                j_add = true;
                count++;
            }

            // Top center pixel 
            if ((i - 1) >= 0)
            {
                r_blue += copy[i - 1][j].rgbtBlue;
                r_green += copy[i - 1][j].rgbtGreen;
                r_red += copy[i - 1][j].rgbtRed;
                count++;

                // Top left pixel
                if (j_min)
                {
                    r_blue += copy[i - 1][j - 1].rgbtBlue;
                    r_green += copy[i - 1][j - 1].rgbtGreen;
                    r_red += copy[i - 1][j - 1].rgbtRed;
                    count++;
                }

                // Top right pixel
                if (j_add)
                {
                    r_blue += copy[i - 1][j + 1].rgbtBlue;
                    r_green += copy[i - 1][j + 1].rgbtGreen;
                    r_red += copy[i - 1][j + 1].rgbtRed;
                    count++;
                }
            }

            // Bottom center pixels
            if ((i + 1) < height)
            {
                r_blue += copy[i + 1][j].rgbtBlue;
                r_green += copy[i + 1][j].rgbtGreen;
                r_red += copy[i + 1][j].rgbtRed;
                count++;

                // Bottom left pixel
                if (j_min)
                {
                    r_blue += copy[i + 1][j - 1].rgbtBlue;
                    r_green += copy[i + 1][j - 1].rgbtGreen;
                    r_red += copy[i + 1][j - 1].rgbtRed;
                    count++;
                }

                // Bottom right pixel
                if (j_add)
                {
                    r_blue += copy[i + 1][j + 1].rgbtBlue;
                    r_green += copy[i + 1][j + 1].rgbtGreen;
                    r_red += copy[i + 1][j + 1].rgbtRed;
                    count++;
                }
            }

            // Calculating the average of each value in a pixel
            float temp = (float)r_blue / count;
            int b = round_up(temp);
            image[i][j].rgbtBlue = b;

            temp = (float)r_green / count;
            b = round_up(temp);
            image[i][j].rgbtGreen = b;

            temp = (float)r_red / count;
            b = round_up(temp);
            image[i][j].rgbtRed = b;
        }
    }
    free(copy);
    return;
}

// Rounds up an integer to the nearest whole number
int round_up(float n)
{
    int calc = n;
    n = n * 10;
    int r = (int)n % 10;

    // Check if first decimal place integer is 5 or greater
    if (r > 4)
    {
        calc = calc + 1;
    }

    return calc;
}

// Truncates values larger than 255 to 255
void capped(int *num)
{
    if (*num > 255)
    {
        *num = 255;
    }
}