#include <stdio.h>
#include <time.h>
#include <stdint.h>

#include "GPIO_handler.h"
#include <errno.h>
#include <gpiod.h>
#include <stdlib.h>
#include <string.h>



int main(){

    // ======== [Definition] =================================== // <- sose gondoltam hogy ezek valaha hasznosak lesznek lol

    printf("Read Started\n");

    // Cuccok a GPIO kezeleshez
	static const char *const chip_path = "/dev/gpiochip0";
	static const unsigned int line_offset = 4;

	struct gpiod_line_request *request;
	enum gpiod_line_value value;
	int ret;

	
    //Cuccok a mintavetelezeshet
    int i;
    uint64_t elapsed_ns;
    struct timespec start, now;
    uint64_t ns = 10 * 1000;

    // 80 + 80 us -> 16 ~ 20 sample
    // 40 bit
    //    50 us low 30 us high (0) or 50 us low 70 us high (1)
    //    Worst case: all high: 120 us -> 12 sample
    // 40 * 12 = 480 sample
    // 480 + 20 -> 500


    // ======== [Trigger] =================================== //


    // ======== [Read] =================================== //
    request = request_input_line(chip_path, line_offset, "get-line-value");
    if (!request) {
		fprintf(stderr, "failed to request line: %s\n",
			strerror(errno));
		return EXIT_FAILURE;
	}
    for ( i = 0; i<520; i++ ){

        clock_gettime(CLOCK_MONOTONIC, &start);
        value = gpiod_line_request_get_value(request, line_offset);
	    printf(value);
        // Read .....
        do {
            clock_gettime(CLOCK_MONOTONIC, &now);
            elapsed_ns = (now.tv_sec - start.tv_sec) * 1000000000L + (now.tv_nsec - start.tv_nsec);
            printf("Wait...\n");
        } while (elapsed_ns < ns);
    }

	/* not strictly required here, but if the app wasn't exiting... */
	gpiod_line_request_release(request);

    return 0;
}