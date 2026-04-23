#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

int main(int argc, char *argv[]) {

    printf("Fake process started\n");
    printf("Arg0: %s\n", argv[0]);

    size_t total = 0;

    while (1) {

        // 🔥 sube RAM más rápido (4 MB en vez de 1 MB)
        for (int i = 0; i < 200; i++) {
            char *block = malloc(1024 * 1024);
            if (!block) return 1;
            memset(block, 'A', 1024 * 1024);
            total++;
        }

        printf("Allocated %zu MB\n", total);
        fflush(stdout);

        // 🔥 CPU más intensa (menos sleep, más cálculo)
        for (volatile long i = 0; i < 150000000; i++);

        // 🔥 sleep más corto = reacción más rápida en tu monitor
        usleep(100000); // 0.1s
    }

    return 0;
}