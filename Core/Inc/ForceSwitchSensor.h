/*
 * SensorCode.h
 *
 *  Created on: Jun 4, 2025
 *      Author: User
 */

#ifndef INC_FORCESWITCHSENSOR_H_
#define INC_FORCESWITCHSENSOR_H_



#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include "stm32l4xx_hal.h"


//force Sensor
#define PI 3.14159265358
#define FSR_THRESHOLD_PRESS   3
#define FSR_THRESHOLD_RELEASE 500
#define DEBOUNCE_DELAY_MS     50
#define WINDOW_SIZE 3
#define MAX_SWITCH_SENSORS 4
#define NUM_SWITCHES 2
//force sensor
//touch switch
#define MAX_TOUCH_SWITCHES 2
#define SHORT_PRESS_THRESHOLD 500   // ms
#define LONG_PRESS_THRESHOLD 1000   // ms
#define MULTI_TAP_WINDOW 300        // ms 同一按鍵快速連按間隔
//touch switch


////力量感測器
typedef enum {
    FSR_RELEASED = 0,
	FSR_PRESSED = 1
} FSR_State;

typedef enum {
    FORCE_ADC_READ_INIT,
	FORCE_ADC_READING,
	FORCE_ADC_READ_DONE
} ForceSensorADCReadState_t;

typedef struct {
	ForceSensorADCReadState_t state;
    uint32_t startTime;
    uint32_t firstStartTime;  // <--- 新增這行
    uint32_t sum;
    uint32_t count;
    uint32_t maxCount;
    int sensorIndex;
    uint32_t average;
} ForceSensorADCReadContext_t;
////力量感測器
////接觸開關
typedef enum {
    TOUCH_IDLE,
    TOUCH_DEBOUNCE,
    TOUCH_PRESSED,
    TOUCH_LONG_PRESSED,
    TOUCH_RELEASED
} TouchState;

typedef struct {
    GPIO_TypeDef* port;
    uint16_t pin;
    TouchState state;
    uint32_t lastChangeTime;
    uint32_t pressStartTime;
    uint8_t tapCount;
    uint32_t lastTapTime;
    bool longPressDetected;
} TouchSwitchContext;
////接觸開關

///整體
typedef struct {
    bool isForceSensor1Enabled;
    bool isForceSensor2Enabled;
    uint32_t forceSensorPressDuration;
    uint32_t forcePressValueThreshold;
    bool isTouchSwitch1Enabled;
    bool isTouchSwitch2Enabled;
    bool isTouchSwitch3Enabled;
    bool isTouchSwitch4Enabled;
    uint32_t touchSwitchDebounceDuration;
} ForceSwitchSensorConfig;

typedef struct {
    bool sensor1;
    bool sensor2;
} TwoBoolResult;
///整體
///////////實體宣告
extern ForceSensorADCReadContext_t fsr1Context;// 宣告變數（告訴編譯器變數在別的地方定義） 不佔用記憶體
extern ForceSensorADCReadContext_t fsr2Context;
//
extern TouchSwitchContext touchSwitches[MAX_TOUCH_SWITCHES];//宣告變數

// 函式宣告 ///力量感測器
void startForceSensorADCRead(ForceSensorADCReadContext_t *context, int sensorIndex, uint32_t sensorPressDuration);
bool processForceSensorADCRead(ForceSensorADCReadContext_t *context);
uint32_t getForceSensorADCReadAverage(ForceSensorADCReadContext_t *context);
bool getAllForceSensorState(bool isSensor1Enabled, bool isSensor2Enabled, uint32_t sensorPressDuration, uint32_t pressureValueThreshold);

// 函式宣告//接觸開關
void initTouchSwitchContext(TouchSwitchContext *ctx, uint8_t sensorIndex, uint32_t debounceDuration);
void processTouchSwitch(TouchSwitchContext *ctx);
void updateTouchSwitchState(TouchSwitchContext* sw, uint32_t debounceTime);
void touchSensor_update(void);  // <- 在這宣告
// 函式宣告 ///整體
TwoBoolResult GetForceSwitchSensor(ForceSwitchSensorConfig config);

#endif /* INC_FORCESWITCHSENSOR_H_ */
