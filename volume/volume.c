// Modifies the volume of an audio file

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

// Number of bytes in .wav header
const int HEADER_SIZE = 44;

int main(int argc, char *argv[])
{
    // Check command-line arguments
    if (argc != 4)
    {
        printf("Usage: \033[1m./volume input.wav output.wav\033[0m \033[4mfactor\033[0m\n");
        return 1;
    }

    // Open files and determine scaling factor
    FILE *input = fopen(argv[1], "r");
    if (input == NULL)
    {
        printf("volume: Could not open input file.\n");
        return 1;
    }

    FILE *output = fopen(argv[2], "w");
    if (output == NULL)
    {
        printf("volume: Could not open output file.\n");
        return 1;
    }

    float factor = atof(argv[3]);
    int16_t b;

    // Copy header from input file to output file
		for (int i = 0; i < 22; i++)
		{
			fread(&b, sizeof(b), 1, input);
			fwrite(&b, sizeof(b), 1, output);
		}

    // Read samples from input file and write updated data to output file

		while ( fread(&b, sizeof(b), 1, input) != 0)
		{
			b *= factor;
			fwrite(&b, sizeof(b), 1, output);
		}

    // Close files
    fclose(input);
    fclose(output);
}
