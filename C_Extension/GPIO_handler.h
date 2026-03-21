#ifndef GPIO_HANDLER_H
#define GPIO_HANDLER_H

#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

//AI generalta nyilvan a exmaple code-ból

// Requests an input line and returns a gpiod_line_request object.
// Returns NULL on failure.
struct gpiod_line_request *request_input_line(const char *chip_path,
					      unsigned int offset,
					      const char *consumer);

// Prints the value of a GPIO line (Active/Inactive).
// Returns EXIT_SUCCESS on success, EXIT_FAILURE on error.
int print_value(unsigned int offset, enum gpiod_line_value value);
// Ez a fos amugy nem megy át valamiért .....

#endif // GPIO_UTILS_H
