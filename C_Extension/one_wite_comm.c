#include <stdio.h>
#include <time.h>
#include <stdint.h>


int main(){
    printf("Read Started\n");


    int pin_id = 4;
    int i;
    uint64_t elapsed_ns;
    struct timespec start, now;
    uint64_t ns = 10 * 1000;

    // https://libgpiod.readthedocs.io/en/latest/core_chips.html
    struct gpiod_chip *chip;
    struct gpiod_line *line; 
    int value;
    chip = gpiod_chip_open("/dev/gpiochip0"); // volt 0,1 és 4 is, gpioinfo parancs kidobja melyik chip melyiket pint kezeli
    if (!chip) {
        perror("Failed to open GPIO chip");
        return 1;
    }

    // Get the GPIO line
    line = gpiod_chip_get_line(chip, pin_id);
    if (!line) {
        perror("Failed to get GPIO line");
        gpiod_chip_close(chip);
        return 1;
    }

    // Set the line as input
    if (gpiod_line_request_input(line, "my_app") < 0) {
        perror("Failed to set line as input");
        gpiod_line_release(line);
        gpiod_chip_close(chip);
        return 1;
    }



    // 80 + 80 us -> 16 ~ 20 sample
    // 40 bit
    //    50 us low 30 us high (0) or 50 us low 70 us high (1)
    //    Worst case: all high: 120 us -> 12 sample
    // 40 * 12 = 480 sample
    // 480 + 20 -> 500


    return 0;
    for ( i = 0; i<520; i++ ){

        clock_gettime(CLOCK_MONOTONIC, &start);
        value = gpiod_line_get_value(line);
        printf("GPIO 17 value: %d\n", value);
        do {
            clock_gettime(CLOCK_MONOTONIC, &now);
            elapsed_ns = (now.tv_sec - start.tv_sec) * 1000000000L + (now.tv_nsec - start.tv_nsec);
            printf("Wait...\n");
        } while (elapsed_ns < ns);
    }
    return 0;


    // Release the line and close the chip
    gpiod_line_release(line);
    gpiod_chip_close(chip);
}