#include <stdint.h>
#include <stddef.h>
uint8_t ti_Open(const char *,const char *);
void *ti_GetDataPtr(uint8_t);
size_t ti_GetSize(uint8_t);
void ti_Close(uint8_t);
