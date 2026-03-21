#include <stdio.h>
#include <time.h>



int main(){
    printf("Read Started");

    int i;
    uint64_t ns = 10 * 1000;
    struct timespec start, now;

    // 80 + 80 us -> 16 ~ 20 sample
    // 40 bit
    //    50 us low 30 us high (0) or 50 us low 70 us high (1)
    //    Worst case: all high: 120 us -> 12 sample
    // 40 * 12 = 480 sample
    // 480 + 20 -> 500

    for ( i = 0; i<520; i++ ){

        clock_gettime(CLOCK_MONOTONIC, &start);
        printf("Iteration %d\n", i);
        do {
            clock_gettime(CLOCK_MONOTONIC, &now);
            uint64_t elapsed_ns = (now.tv_sec - start.tv_sec) * 1000000000L + (now.tv_nsec - start.tv_nsec);
        } while (elapsed_ns < ns);
    }
    return 0;
}