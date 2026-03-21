#ifndef GPIO_HANDLER_H
#define GPIO_HANDLER_H

#include <gpiod.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>

struct gpiod_line_request *request_output_line(const char *chip_path, unsigned int offset, enum gpiod_line_value value, const char *consumer);
struct gpiod_line_request *request_input_line(const char *chip_path, unsigned int offset, const char *consumer);
int print_value(unsigned int offset, enum gpiod_line_value value);

#endif // GPIO_UTILS_H
