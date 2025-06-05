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


/* USER CODE BEGIN PM */
#define PI 3.14159265358
#define FSR_THRESHOLD_PRESS   3
#define FSR_THRESHOLD_RELEASE 500
#define DEBOUNCE_DELAY_MS     50
#define WINDOW_SIZE 3
/* USER CODE END PM */
typedef enum {
    FSR_RELEASED = 0,
	FSR_PRESSED = 1
} FSR_State;

typedef enum {
    ADC_READ_INIT,
    ADC_READING,
    ADC_READ_DONE
} ADCReadState_t;

typedef struct {
    ADCReadState_t state;
    uint32_t startTime;
    uint32_t sum;
    uint32_t count;
    uint32_t maxCount;
    int sensorIndex;
    uint32_t average;
} ADCReadContext_t;

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

extern ADCReadContext_t fsr1Context;
extern ADCReadContext_t fsr2Context;


// 函式宣告
TwoBoolResult GetForceSwitchSensor(ForceSwitchSensorConfig config);
void startADCRead(ADCReadContext_t *context, int sensorIndex, uint32_t sensorPressDuration);
bool processADCRead(ADCReadContext_t *context);
uint32_t getADCReadAverage(ADCReadContext_t *context);
bool getAllForceSensorState(bool isSensor1Enabled, bool isSensor2Enabled, uint32_t sensorPressDuration, uint32_t pressureValueThreshold);

#endif /* INC_FORCESWITCHSENSOR_H_ */
