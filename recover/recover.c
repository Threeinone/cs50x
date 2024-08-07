#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

bool header_check(uint8_t *block);
 
int main(int argc, char *argv[])
{
	if (argc != 2) 
	{
		printf("recover: incorrect number of arguments.\n\tusage: ./recover card.card\n");
		return 1;
	}
	
	FILE *card = fopen(argv[1], "r");
	if (card == NULL)
	{
		printf("recover: could not open file\n");
		return 1;
	}

	char filename[10];
	int jpg_counter = 0;

	FILE *active_file = NULL;

	uint8_t block[512]; 
	bool start = true;

	while (fread(block, 512, 1, card) != 0)
	{
		if (header_check(block)) // new jpeg
		{

			if (start)
			{
				sprintf(filename, "%03i.jpg", jpg_counter);
				active_file = fopen(filename, "w");
				fwrite(block, sizeof(block), 1, active_file);
				start = false;

			} else {
				jpg_counter++;

				if (jpg_counter > 999)
				{
					printf("recover: file recovery limit reached");
					return 1;
				}

				fclose(active_file);
				sprintf(filename, "%03i.jpg", jpg_counter);
				active_file = fopen(filename, "w");
				fwrite(block, sizeof(block), 1, active_file);
			}

		} else if (active_file) { // if already found jpeg
			fwrite(block, sizeof(block), 1, active_file);
		}
	}
	
	fclose(card);
	if (active_file)
		fclose(active_file);
	return 0;
}

bool header_check(uint8_t *block)
{
	bool returnval = true;
	uint8_t bytes[] = {0xff, 0xd8, 0xff};

	for (int i = 0; i < 3; i++)
	{
		if (block[i] != bytes[i])
			returnval = false;
	}
	if ((block[3] & 0xf0) != 0xe0)
		returnval = false;
	return returnval;
}
