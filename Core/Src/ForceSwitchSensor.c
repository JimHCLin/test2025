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
//int index = 0;
int count = 0;
int x=0;
extern uint8_t ledTrigger;
extern uint32_t lastDebounceTime;

FSR_State fsrState = FSR_RELEASED;


//
ForceSensorADCReadContext_t fsr1Context = {0};
ForceSensorADCReadContext_t fsr2Context = {0};

//////////////////////////////////
void lightOnLED(void)
{
	//int count=0;
	//int statusLED=0;
	HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    //state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);
    //HAL_Delay(100);
}
void lightOffLED(void)
{
	//int count=0;
	//int statusLED=0;

    //將 PB8 Off
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    //state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);
    //receive_data_uart();
    //HAL_Delay(100);
    //i++;
}
uint16_t readSingleForceSensorADCValue(int sensorIndex)
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

void startForceSensorADCRead(ForceSensorADCReadContext_t *context, int sensorIndex, uint32_t sensorPressDuration)
{
    (*context).sensorIndex = sensorIndex;
    (*context).maxCount = sensorPressDuration / 10;
    if ((*context).maxCount == 0) (*context).maxCount = 1; // 防除以0
    (*context).sum = 0;
    (*context).count = 0;
    (*context).state = FORCE_ADC_READ_INIT;
}

bool processForceSensorADCRead(ForceSensorADCReadContext_t *context)
{
    switch ((*context).state)
    {
        case FORCE_ADC_READ_INIT:
        	//
        	(*context).firstStartTime = HAL_GetTick();
			(*context).startTime = (*context).firstStartTime;
			(*context).sum = 0;
			(*context).count = 0;
			(*context).state = FORCE_ADC_READING;
            //(*context).state = FORCE_ADC_READING;
            break;

        case FORCE_ADC_READING:
        	int a=HAL_GetTick();
            if (HAL_GetTick() - (*context).startTime >= 10)  // 間隔10ms讀一次
            {
                uint16_t valueADC = readSingleForceSensorADCValue((*context).sensorIndex);
                (*context).sum += valueADC;
                (*context).count++;
                (*context).startTime = HAL_GetTick(); // 重設計時
                if ((*context).count >= (*context).maxCount)
                {
                    (*context).average = (*context).sum / (*context).count;
                    (*context).state = FORCE_ADC_READ_DONE;
                }
            }
            // ✅ 加入 timeout 條件
			if (HAL_GetTick() - (*context).firstStartTime >= (*context).maxCount * 10)
			{
				if ((*context).count > 0) {
					(*context).average = (*context).sum / (*context).count;
				} else {
					(*context).average = 0;
				}
				(*context).state = FORCE_ADC_READ_DONE;
			}
            break;

        case FORCE_ADC_READ_DONE:
            return true;  // 完成讀取了

        default:
            break;
    }
    return false;  // 尚未完成
}

uint32_t getForceSensorADCReadAverage(ForceSensorADCReadContext_t *context)
{
    return (*context).average;
}


//


bool getAllForceSensorState(bool isSensor1Enabled ,bool isSensor2Enabled ,uint32_t sensorPressDuration,uint32_t pressureValueThreshold)
{

	/////////// 這個函式只執行一次,他會用阻塞式的方式等兩個sensor 都做完後 才會跳出去///
	// 但是這兩個sensor在讀資料時,是用非阻塞的方式
	//所以每個 sensor 要讀100ms ,但這個函式執行完成,整體時間只有100ms
	bool allForceSensorStateResult = false;
	uint32_t forceSensor1AveragedValue = 0;
	uint32_t forceSensor2AveragedValue = 0;
	bool fsr1Done = false;
	bool fsr2Done = false;
	uint32_t startTime = HAL_GetTick();
	// 啟動需要的感測器
	if (isSensor1Enabled) {
		startForceSensorADCRead(&fsr1Context, 1, sensorPressDuration);
		fsr1Done = false;
	} else {
		fsr1Done = true;  // 不啟用就視為已完成
	}

	if (isSensor2Enabled) {
		startForceSensorADCRead(&fsr2Context, 2, sensorPressDuration);
		fsr2Done = false;
	} else {
		fsr2Done = true;  // 不啟用就視為已完成
	}

	// 非阻塞等待兩個感測器都完成
	while (!fsr1Done || !fsr2Done)
	{
		if (!fsr1Done && processForceSensorADCRead(&fsr1Context)) {
			forceSensor1AveragedValue = getForceSensorADCReadAverage(&fsr1Context);
			fsr1Done = true;
		}

		if (!fsr2Done && processForceSensorADCRead(&fsr2Context)) {
			forceSensor2AveragedValue = getForceSensorADCReadAverage(&fsr2Context);
			fsr2Done = true;
		}

		// ✅ 可插入其他非阻塞任務
	}

	// 比較是否有達到閾值
	if ((isSensor1Enabled && forceSensor1AveragedValue > pressureValueThreshold) ||
		(isSensor2Enabled && forceSensor2AveragedValue > pressureValueThreshold)) {
		allForceSensorStateResult = true;
		lightOnLED();
		//HAL_Delay(200);
		//lightOffLED();
	}
	else
	{
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


bool checkSwitchState(int sensorIndex, uint32_t switchDebounceDuration)
{
    static uint32_t lastDebounceTime[MAX_SWITCH_SENSORS] = {0};
    static GPIO_PinState currentState[MAX_SWITCH_SENSORS] = {GPIO_PIN_SET, GPIO_PIN_SET, GPIO_PIN_SET, GPIO_PIN_SET};
    static GPIO_PinState lastButtonState[MAX_SWITCH_SENSORS] = {GPIO_PIN_SET, GPIO_PIN_SET, GPIO_PIN_SET, GPIO_PIN_SET};
    bool isTouchSwitchPressed = false;

    if(sensorIndex < 1 || sensorIndex > MAX_SWITCH_SENSORS) {
        // 無效的 sensorIndex，直接回傳 false
        return false;
    }

    uint16_t pin = 0;
    switch(sensorIndex) {
        case 1:
        	pin = GPIO_PIN_8;
        	break;//GPIO_PIN_8 代表第 8 位元是1(從右邊開始數第九個數字)，二進位是 0000 0001 0000 0000 (十進位 256)
        case 2: pin = GPIO_PIN_6; break;
        case 3: pin = GPIO_PIN_9; break;
        case 4: pin = GPIO_PIN_5; break;
    }

    //GPIO_PinState currentState = HAL_GPIO_ReadPin(GPIOC, pin);

    // sensorIndex 從 1 開始，陣列從 0 開始，所以要 -1
    int idx = sensorIndex - 1;
    currentState[idx] = HAL_GPIO_ReadPin(GPIOC, pin);
    //currentState
    if(currentState[idx] != lastButtonState[idx]) {
        lastDebounceTime[idx] = HAL_GetTick();
    }
    uint32_t timeNow=HAL_GetTick();
    uint32_t elapsed = timeNow - lastDebounceTime[idx];
    if(elapsed > switchDebounceDuration) {
        if(currentState[idx] == GPIO_PIN_RESET) {
            isTouchSwitchPressed = true;
        }
    }

    lastButtonState[idx] = currentState[idx];

    return isTouchSwitchPressed;
}
bool getAllTouchSwitchState(bool isSwitch1Enabled,bool isSwitch2Enabled,bool isSwitch3Enabled,bool isSwitch4Enabled,uint32_t touchSwitchDebounceDuration)
{
	bool switchEnabled[NUM_SWITCHES] = { isSwitch1Enabled, isSwitch2Enabled, isSwitch3Enabled, isSwitch4Enabled };
	bool allTouchSwitchStateResult=false;
	//bool isTouchSwitch1Pressed = true;  // 開關1被按下
	bool isTouchSwitch1Pressed = false; // 開關1沒被按下
	bool isTouchSwitch2Pressed = false;
	bool isTouchSwitch3Pressed = false;
	bool isTouchSwitch4Pressed = false;
	uint8_t forceSensor2AveragedaValue=0;
	uint8_t disabledCount = 0;
	bool switchPressed[NUM_SWITCHES] = { isTouchSwitch1Pressed,isTouchSwitch2Pressed ,isTouchSwitch3Pressed ,isTouchSwitch4Pressed }; // 儲存各按鈕是否被按下
	uint8_t enabledSwitchIndices[NUM_SWITCHES]={0};
	uint8_t enabledSwitchCount=0;
	uint8_t pressedCount=0;
	for(int i=0;i<NUM_SWITCHES;i++)
	{
		if(switchEnabled[i])
		{
			enabledSwitchIndices[enabledSwitchCount++]=i+1;// // 儲存 switch 編號（從 1 開始）
		}
	}
	//enabledSwitchCount = 3

	//enabledSwitchIndices = {2, 3, 4} 第2 ,第3和第4個 sensor有啟動
	///////////////////////////////////
	uint32_t startTime = HAL_GetTick();
	for(int i=0;i<2;i++)//i=0==>會進去delay,i=1 ==>不會進去delay
	{
		///
		for(int j=0;j<enabledSwitchCount;j++)
		{
			////enabledSwitchIndices=[1,2,3,4];
			//switchPressed[i]=checkSwitchState(enabledSwitchIndices[i],touchSwitchDebounceDuration);
			switchPressed[enabledSwitchIndices[j]-1]=checkSwitchState(enabledSwitchIndices[j],touchSwitchDebounceDuration);
			if(switchPressed[enabledSwitchIndices[j] - 1] && (i == 1))
			{
				pressedCount++;
			}
		}
		///
		//isTouchSwitch1Pressed=checkSwitchState(1,touchSwitchDebounceDuration);
		//isTouchSwitch2Pressed=checkSwitchState(2,touchSwitchDebounceDuration);//再改成2
		//isTouchSwitch3Pressed=checkSwitchState(3,touchSwitchDebounceDuration);
		//isTouchSwitch4Pressed=checkSwitchState(4,touchSwitchDebounceDuration);
		if (i == 0)
		{
			HAL_Delay(100); // 只在第一次檢查後延遲
		}
		//HAL_Delay(100); // 每10毫秒檢查一次按鈕狀態
		//isTouchSwitch1Pressed=pressed;
	}
	uint32_t endTime = HAL_GetTick();
	uint32_t Duration = endTime - startTime;
	//uint8_t pressedFinalCount=pressedCount/2;// 因為for
	//int a=0;
	//////////////////////////////////

    /*
	if (enabledSwitchCount == 4)
	{   //四個開關都啟用
		//堵塞作法
		uint32_t startTime = HAL_GetTick();
		for(int i=0;i<2;i++)//i=0==>會進去delay,i=1 ==>不會進去delay
		{
			///
			for(int i=0;i<enabledSwitchCount;i++)
			{
				////enabledSwitchIndices=[1,2,3,4];
				//switchPressed[i]=checkSwitchState(enabledSwitchIndices[i],touchSwitchDebounceDuration);
				switchPressed[enabledSwitchIndices[i]-1]=checkSwitchState(enabledSwitchIndices[i],touchSwitchDebounceDuration);
			}
			///
			//isTouchSwitch1Pressed=checkSwitchState(1,touchSwitchDebounceDuration);
			//isTouchSwitch2Pressed=checkSwitchState(2,touchSwitchDebounceDuration);//再改成2
			//isTouchSwitch3Pressed=checkSwitchState(3,touchSwitchDebounceDuration);
			//isTouchSwitch4Pressed=checkSwitchState(4,touchSwitchDebounceDuration);
			if (i == 0)
			{
				HAL_Delay(100); // 只在第一次檢查後延遲
			}
			//HAL_Delay(100); // 每10毫秒檢查一次按鈕狀態
			//isTouchSwitch1Pressed=pressed;
		}
		uint32_t endTime = HAL_GetTick();
		uint32_t Duration = endTime - startTime;
		//堵塞作法
		//////
		/*
		//非堵塞作法

		//計算時間
		uint32_t startTimeNonBlock = HAL_GetTick();
		////////////
		uint32_t switchScanInterval=touchSwitchDebounceDuration/2;
		static uint32_t lastSwitchScanTime   = 0;
		if (HAL_GetTick() - lastSwitchScanTime  >= switchScanInterval)  // 每 10ms 掃一次
		{
			isTouchSwitch1Pressed = checkSwitchState(1, touchSwitchDebounceDuration);
			isTouchSwitch2Pressed = checkSwitchState(2, touchSwitchDebounceDuration);
			//isTouchSwitch3Pressed = checkSwitchState(3, touchSwitchDebounceDuration);
			//isTouchSwitch4Pressed = checkSwitchState(4, touchSwitchDebounceDuration);

			lastSwitchScanTime  = HAL_GetTick();  // 更新時間
		}
		//////////
		uint32_t endTimeNonBlock = HAL_GetTick();
		uint32_t DurationNonBlock = endTimeNonBlock - startTimeNonBlock;

		//非堵塞作法


	}
	else if (enabledSwitchCount == 3)
	{
		//堵塞作法
		uint32_t startTime = HAL_GetTick();
		for(int i=0;i<2;i++)
		{
			///
			for(int i=0;i<enabledSwitchCount;i++)
			{
				//i=0,1,2
				//enabledSwitchIndices=[1,3,4];
				switchPressed[enabledSwitchIndices[i]-1]=checkSwitchState(enabledSwitchIndices[i],touchSwitchDebounceDuration);
			}
			///
			//isTouchSwitch1Pressed=checkSwitchState(1,touchSwitchDebounceDuration);
			//isTouchSwitch2Pressed=checkSwitchState(2,touchSwitchDebounceDuration);//再改成2
			//isTouchSwitch3Pressed=checkSwitchState(3,touchSwitchDebounceDuration);
			//isTouchSwitch4Pressed=checkSwitchState(4,touchSwitchDebounceDuration);
			if (i == 0)
			{
				HAL_Delay(100); // 只在第一次檢查後延遲
			}
			//HAL_Delay(100); // 每10毫秒檢查一次按鈕狀態
			//isTouchSwitch1Pressed=pressed;
		}
		uint32_t endTime = HAL_GetTick();
		uint32_t Duration = endTime - startTime;
		//堵塞作法
	}
	else if (enabledSwitchCount == 2)
	{
		printf("兩個 switch 不啟用\n");
		printf("啟用的 switch 有：");
		if (isSwitch1Enabled) printf("Switch1 ");
		if (isSwitch2Enabled) printf("Switch2 ");
		if (isSwitch3Enabled) printf("Switch3 ");
		if (isSwitch4Enabled) printf("Switch4 ");

	}
	else if (enabledSwitchCount == 1) {
		printf("三個 switch 不啟用\n");
		printf("啟用的 switch 有：");
		if (isSwitch1Enabled) printf("Switch1 ");
		if (isSwitch2Enabled) printf("Switch2 ");
		if (isSwitch3Enabled) printf("Switch3 ");
		if (isSwitch4Enabled) printf("Switch4 ");

	}
	else if (enabledSwitchCount == 0) {
		printf("全部 switch 都不啟用\n");

	}
	else {
		printf("狀況不明\n");
	}
	*/
	////////////////////////////////////////////////////////////

	//int pressedCount = isTouchSwitch1Pressed + isTouchSwitch2Pressed + isTouchSwitch3Pressed + isTouchSwitch4Pressed;
	if (pressedCount >= 1) {
	    // 上面再改成2
		allTouchSwitchStateResult=true;
		lightOnLED();//1個以上開關按下 就亮燈
	}
	else
	{
	    // 開關1沒被按下要做的事
		lightOffLED();//沒開關按下
	}
	return allTouchSwitchStateResult;
}

