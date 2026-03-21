#ifndef GPIO_UTILS_H
#define GPIO_UTILS_H

#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

// Requests an input line and returns a gpiod_line_request object.
// Returns NULL on failure.
struct gpiod_line_request *request_input_line(const char *chip_path,
					      unsigned int offset,
					      const char *consumer);

//AI generalta nyilvan a exmaple code-ból

#endif // GPIO_UTILS_H
