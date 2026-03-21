#include <stdio.h>
#include <time.h>
#include <stdint.h>
#include <gpiod.h>


#include <errno.h>
#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Request a line as input. */
static struct gpiod_line_request *request_input_line(const char *chip_path,
						     unsigned int offset,
						     const char *consumer)
{
	struct gpiod_request_config *req_cfg = NULL;
	struct gpiod_line_request *request = NULL;
	struct gpiod_line_settings *settings;
	struct gpiod_line_config *line_cfg;
	struct gpiod_chip *chip;
	int ret;

	chip = gpiod_chip_open(chip_path);
	if (!chip)
		return NULL;

	settings = gpiod_line_settings_new();
	if (!settings)
		goto close_chip;

	gpiod_line_settings_set_direction(settings, GPIOD_LINE_DIRECTION_INPUT);

	line_cfg = gpiod_line_config_new();
	if (!line_cfg)
		goto free_settings;

	ret = gpiod_line_config_add_line_settings(line_cfg, &offset, 1,
						  settings);
	if (ret)
		goto free_line_config;

	if (consumer) {
		req_cfg = gpiod_request_config_new();
		if (!req_cfg)
			goto free_line_config;

		gpiod_request_config_set_consumer(req_cfg, consumer);
	}

	request = gpiod_chip_request_lines(chip, req_cfg, line_cfg);

	gpiod_request_config_free(req_cfg);

free_line_config:
	gpiod_line_config_free(line_cfg);

free_settings:
	gpiod_line_settings_free(settings);

close_chip:
	gpiod_chip_close(chip);

	return request;
}

static int print_value(unsigned int offset, enum gpiod_line_value value)
{
	if (value == GPIOD_LINE_VALUE_ACTIVE)
		printf("%d=Active\n", offset);
	else if (value == GPIOD_LINE_VALUE_INACTIVE) {
		printf("%d=Inactive\n", offset);
	} else {
		fprintf(stderr, "error reading value: %s\n",
			strerror(errno));
		return EXIT_FAILURE;
	}

	return EXIT_SUCCESS;
}

int main(void)
{
	/* Example configuration - customize to suit your situation. */
	static const char *const chip_path = "/dev/gpiochip0";
	static const unsigned int line_offset = 5;

	struct gpiod_line_request *request;
	enum gpiod_line_value value;
	int ret;

	request = request_input_line(chip_path, line_offset, "get-line-value");
	if (!request) {
		fprintf(stderr, "failed to request line: %s\n",
			strerror(errno));
		return EXIT_FAILURE;
	}

	value = gpiod_line_request_get_value(request, line_offset);
	ret = print_value(line_offset, value);

	/* not strictly required here, but if the app wasn't exiting... */
	gpiod_line_request_release(request);

	return ret;
}


//int main(){
//    printf("Read Started\n");
//
//
//    int pin_id = 4;
//    int i;
//    uint64_t elapsed_ns;
//    struct timespec start, now;
//    uint64_t ns = 10 * 1000;
//
//    // https://libgpiod.readthedocs.io/en/latest/core_chips.html
//    struct gpiod_chip *chip;
//    struct gpiod_line *line; 
//    int value;
//    chip = gpiod_chip_open("/dev/gpiochip0"); // volt 0,1 és 4 is, gpioinfo parancs kidobja melyik chip melyiket pint kezeli
//    if (!chip) {
//        perror("Failed to open GPIO chip");
//        return 1;
//    }
//
//    // Get the GPIO line
//    line = gpiod_chip_get_line(chip, pin_id);
//    if (!line) {
//        perror("Failed to get GPIO line");
//        gpiod_chip_close(chip);
//        return 1;
//    }
//
//    // Set the line as input
//    if (gpiod_line_request_input(line, "my_app") < 0) {
//        perror("Failed to set line as input");
//        gpiod_line_release(line);
//        gpiod_chip_close(chip);
//        return 1;
//    }
//
//
//
//    // 80 + 80 us -> 16 ~ 20 sample
//    // 40 bit
//    //    50 us low 30 us high (0) or 50 us low 70 us high (1)
//    //    Worst case: all high: 120 us -> 12 sample
//    // 40 * 12 = 480 sample
//    // 480 + 20 -> 500
//
//
//    return 0;
//    for ( i = 0; i<520; i++ ){
//
//        clock_gettime(CLOCK_MONOTONIC, &start);
//        value = gpiod_line_get_value(line);
//        printf("GPIO 17 value: %d\n", value);
//        do {
//            clock_gettime(CLOCK_MONOTONIC, &now);
//            elapsed_ns = (now.tv_sec - start.tv_sec) * 1000000000L + (now.tv_nsec - start.tv_nsec);
//            printf("Wait...\n");
//        } while (elapsed_ns < ns);
//    }
//    return 0;
//
//
//    // Release the line and close the chip
//    gpiod_line_release(line);
//    gpiod_chip_close(chip);
//}