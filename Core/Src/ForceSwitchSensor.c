/*
 * SensorCode.c
 *
 *  Created on: Jun 4, 2025
 *      Author: User
 */

#include <ForceSwitchSensor.h>  // 引用標頭檔
#include "main.h"
#include <stdbool.h>



//////////////////

extern ADC_HandleTypeDef hadc1;
extern ADC_HandleTypeDef hadc2;

//
int i = 0;
int state=0;
int buffer[WINDOW_SIZE] = {0};
int index = 0;
int count = 0;
int x=0;
extern uint8_t ledTrigger;
extern uint32_t lastDebounceTime;

FSR_State fsrState = FSR_RELEASED;


//
ADCReadContext_t fsr1Context = {0};
ADCReadContext_t fsr2Context = {0};

//////////////////////////////////
void lightOnLED(void)
{
	//int count=0;
	//int statusLED=0;
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    //state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);
    HAL_Delay(100);
}
void lightOffLED(void)
{
	//int count=0;
	//int statusLED=0;

    //將 PB8 Off
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    //state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);
    //receive_data_uart();
    HAL_Delay(100);
    //i++;
}
uint16_t readSingleADCValue(int sensorIndex)
{
    HAL_StatusTypeDef status;
    uint16_t adcValue = 0;
    ADC_HandleTypeDef* hadc = NULL;

    // 根據 sensorIndex 選擇對應 ADC
    if (sensorIndex == 1) {
        hadc = &hadc1;
    } else if (sensorIndex == 2) {
        hadc = &hadc2;
    } else {
    	Error_Handler();  // 加入錯誤處理
        return 0; // 無效的 index
    }

    // 啟動 ADC
    status = HAL_ADC_Start(hadc);
    if (status != HAL_OK) {
        return 0; // 啟動失敗
    }

    // 輪詢等待轉換完成
    status = HAL_ADC_PollForConversion(hadc, 10);
    if (status == HAL_OK) {
        adcValue = HAL_ADC_GetValue(hadc);
    }

    return adcValue;
}

void startADCRead(ADCReadContext_t *context, int sensorIndex, uint32_t sensorPressDuration)
{
    (*context).sensorIndex = sensorIndex;
    (*context).maxCount = sensorPressDuration / 10;
    if ((*context).maxCount == 0) (*context).maxCount = 1; // 防除以0
    (*context).sum = 0;
    (*context).count = 0;
    (*context).state = ADC_READ_INIT;
}

bool processADCRead(ADCReadContext_t *context)
{
    switch ((*context).state)
    {
        case ADC_READ_INIT:
            (*context).startTime = HAL_GetTick();
            (*context).state = ADC_READING;
            break;

        case ADC_READING:
            if (HAL_GetTick() - (*context).startTime >= 10)  // 間隔10ms讀一次
            {
                uint16_t valueADC = readSingleADCValue((*context).sensorIndex);
                (*context).sum += valueADC;
                (*context).count++;
                (*context).startTime = HAL_GetTick(); // 重設計時
                if ((*context).count >= (*context).maxCount)
                {
                    (*context).average = (*context).sum / (*context).count;
                    (*context).state = ADC_READ_DONE;
                }
            }
            break;

        case ADC_READ_DONE:
            return true;  // 完成讀取了

        default:
            break;
    }
    return false;  // 尚未完成
}

uint32_t getADCReadAverage(ADCReadContext_t *context)
{
    return (*context).average;
}


//

uint32_t readAveragedFSR(int sensorIndex,uint32_t sensorPressDuration)
{
	//非阻塞

	 ADCReadContext_t adcContext = {0};

	startADCRead(&adcContext, sensorIndex, sensorPressDuration);

	while (!processADCRead(&adcContext))
	{
		// 可在這裡執行其他任務，非阻塞
	}

	return getADCReadAverage(&adcContext);

    /*
	//阻塞
	//sensorPressDuration=30;

	uint32_t sum = 0;
	uint32_t average = 0;
	uint32_t count = 0;
	count=sensorPressDuration/10;
    if (sensorPressDuration == 0)
    {
    	return 0;
    }
    for (uint32_t i = 0; i < count; i++)
    {
    	//count=3
    	//i=0, 1 2
        uint16_t valueADC = readSingleADCValue(sensorIndex); // 假設ADC為16-bit
        sum += valueADC;
        HAL_Delay(10);
    }
    average=sum / count;


    //return average;
     */

}
bool getAllForceSensorState(bool isSensor1Enabled ,bool isSensor2Enabled ,uint32_t sensorPressDuration,uint32_t pressureValueThreshold)
	{

		/////////// 這個函式只執行一次,他會用阻塞式的方式等兩個sensor 都做完後 才會跳出去
		// 但是這兩個sensor在讀資料時,是用非阻塞的方式
		//所以每個 sensor 要讀100ms ,但這個函式執行完橫,整體時間只有100ms
		bool allForceSensorStateResult = false;
		uint32_t forceSensor1AveragedValue = 0;
		uint32_t forceSensor2AveragedValue = 0;
		bool fsr1Done = false;
		bool fsr2Done = false;
		uint32_t startTime = HAL_GetTick();
		// 啟動需要的感測器
		if (isSensor1Enabled) {
			startADCRead(&fsr1Context, 1, sensorPressDuration);
			fsr1Done = false;
		} else {
			fsr1Done = true;  // 不啟用就視為已完成
		}

		if (isSensor2Enabled) {
			startADCRead(&fsr2Context, 2, sensorPressDuration);
			fsr2Done = false;
		} else {
			fsr2Done = true;  // 不啟用就視為已完成
		}

		// 非阻塞等待兩個感測器都完成
		while (!fsr1Done || !fsr2Done)
		{
			if (!fsr1Done && processADCRead(&fsr1Context)) {
				forceSensor1AveragedValue = getADCReadAverage(&fsr1Context);
				fsr1Done = true;
			}

			if (!fsr2Done && processADCRead(&fsr2Context)) {
				forceSensor2AveragedValue = getADCReadAverage(&fsr2Context);
				fsr2Done = true;
			}

			// ✅ 可插入其他非阻塞任務
		}

		// 比較是否有達到閾值
		if ((isSensor1Enabled && forceSensor1AveragedValue > pressureValueThreshold) ||
			(isSensor2Enabled && forceSensor2AveragedValue > pressureValueThreshold)) {
			allForceSensorStateResult = true;
			lightOnLED();
			HAL_Delay(200);
			lightOffLED();
		}
		return allForceSensorStateResult;
	}

TwoBoolResult GetForceSwitchSensor(ForceSwitchSensorConfig config)
{
	TwoBoolResult result;

	//
	// 取得 config 裡的成員
	// 取出九個參數
	bool isForceSensor1Enabled = config.isForceSensor1Enabled;
	bool isForceSensor2Enabled = config.isForceSensor2Enabled;
	uint32_t forceSensorPressDuration = config.forceSensorPressDuration;
	uint32_t forcePressValueThreshold = config.forcePressValueThreshold;
	bool isTouchSwitch1Enabled = config.isTouchSwitch1Enabled;
	bool isTouchSwitch2Enabled = config.isTouchSwitch2Enabled;
	bool isTouchSwitch3Enabled = config.isTouchSwitch3Enabled;
	bool isTouchSwitch4Enabled = config.isTouchSwitch4Enabled;
	uint32_t touchSwitchDebounceDuration = config.touchSwitchDebounceDuration;
	// 全部力量感測器回傳值
	bool forceSensorFinalState=false;


	// Final result of all switches
	bool touchSwitchFinalState = false;

	result.sensor1 = forceSensorFinalState;
	result.sensor2 = touchSwitchFinalState;
	//
	//while(1)
	//{
		lightOnLED();
		HAL_Delay(300);
		lightOffLED();

		// 全部力量感測器回傳值
		//bool forceSensorFinalState=false;
		//從flash讀取力量感測器初始參數
		//bool isforceSensor1Enabled=true;
		//bool isforceSensor2Enabled=true;
				//
		//uint32_t forceSensorPressDuration = 100;
	    //uint32_t forcepPressValueThreshold = 3000; //


		// 從flash讀取Touch switch enabled flags 初始參數
		//bool isTouchSwitch1Enabled = true;
		//bool isTouchSwitch2Enabled = true;
		//bool isTouchSwitch3Enabled = true;
		//bool isTouchSwitch4Enabled = true;
		// Touch switch behavior parameters
		//uint32_t touchSwitchDebounceDuration = 100;
		//uint32_t touchSwitchPressThreshold = 3000;

		// Final result of all switches
		//bool touchSwitchFinalState = false;

		//讀取所有力量感測器數值
		uint32_t forceSensorStartTime = HAL_GetTick();
		forceSensorFinalState=getAllForceSensorState(isForceSensor1Enabled,isForceSensor2Enabled,forceSensorPressDuration,forcePressValueThreshold);
		uint32_t forceSensorEndTime = HAL_GetTick();
		uint32_t forceSensorDuration = forceSensorEndTime - forceSensorStartTime;

		return result;

    //}
}
