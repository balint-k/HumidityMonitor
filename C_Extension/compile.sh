
gcc GPIO_handler.c one_wite_comm.c -o my_program $(pkg-config --cflags --libs libgpiod)
