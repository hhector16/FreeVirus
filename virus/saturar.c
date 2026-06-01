#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    size_t total = 0;

    while (1) {


        for (int i = 0; i < 200; i++) {

            char *block = malloc(1024 * 1024);

            if (!block) {
                printf("malloc failed after %zu MB allocated\n", total);
                return 1;
            }

            memset(block, 'A', 1024 * 1024);

            total++;

            printf("[+] Allocated: %zu MB\n", total);

            fflush(stdout);
        }

    }

    return 0;
}