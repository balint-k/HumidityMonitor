
gcc GPIO_handler.c one_wite_comm.c -o start_comm $(pkg-config --cflags --libs libgpiod)
