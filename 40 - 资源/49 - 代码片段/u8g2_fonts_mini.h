#ifndef __U8G2_FONTS_MINI_H
#define __U8G2_FONTS_MINI_H

#include <stdint.h>

/**
 * @brief 极简字体库外部声明
 * 这些数据实际存储在 u8g2_fonts_mini.c 的 Flash 空间中
 */

// 1. 复古等宽数字字体 (仅包含数字和少量符号)
extern const uint8_t u8g2_font_amstrad_cpc_extended_8n[];

// 2. 5x7 像素极小字体 (全 ASCII 字符)
extern const uint8_t u8g2_font_5x7_tf[];

// 3. 8x13 像素标准字体 (全 ASCII 字符)
extern const uint8_t u8g2_font_8x13_tf[];

#endif
