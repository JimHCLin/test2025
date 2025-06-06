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


/* USER CODE BEGIN PM */
#define PI 3.14159265358
#define FSR_THRESHOLD_PRESS   3
#define FSR_THRESHOLD_RELEASE 500
#define DEBOUNCE_DELAY_MS     50
#define WINDOW_SIZE 3
#define MAX_SWITCH_SENSORS 4
#define NUM_SWITCHES 2
/* USER CODE END PM */
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
    TOUCH_SWITCH_IDLE,
    TOUCH_SWITCH_DEBOUNCING,
    TOUCH_SWITCH_PRESSED
} TouchSwitchState;

typedef struct {
    uint8_t sensorIndex;
    uint32_t debounceDuration;
    uint32_t lastChangeTime;
    GPIO_PinState lastRawState;
    TouchSwitchState state;
    bool isPressed;
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
extern ForceSensorADCReadContext_t fsr1Context;
extern ForceSensorADCReadContext_t fsr2Context;

// 函式宣告 ///力量感測器
void startForceSensorADCRead(ForceSensorADCReadContext_t *context, int sensorIndex, uint32_t sensorPressDuration);
bool processForceSensorADCRead(ForceSensorADCReadContext_t *context);
uint32_t getForceSensorADCReadAverage(ForceSensorADCReadContext_t *context);
bool getAllForceSensorState(bool isSensor1Enabled, bool isSensor2Enabled, uint32_t sensorPressDuration, uint32_t pressureValueThreshold);

// 函式宣告//接觸開關
void initTouchSwitchContext(TouchSwitchContext *ctx, uint8_t sensorIndex, uint32_t debounceDuration);
void processTouchSwitch(TouchSwitchContext *ctx);

// 函式宣告 ///整體
TwoBoolResult GetForceSwitchSensor(ForceSwitchSensorConfig config);

#endif /* INC_FORCESWITCHSENSOR_H_ */
