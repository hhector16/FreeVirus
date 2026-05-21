#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    size_t total = 0;

    while (1) {

        // in this loop we alloc lots of memory without making it free

        for (int i = 0; i < 200; i++) {
            char *block = malloc(1024 * 1024);
            if (!block) return 1;
            memset(block, 'A', 1024 * 1024);
            total++;
        }

    }

    return 0;
}