/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdbool.h>

/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */
#define PI 3.14159265358
#define FSR_THRESHOLD_PRESS   3
#define FSR_THRESHOLD_RELEASE 500
#define DEBOUNCE_DELAY_MS     50
#define WINDOW_SIZE 3
/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
ADC_HandleTypeDef hadc1;
ADC_HandleTypeDef hadc2;

I2C_HandleTypeDef hi2c1;

UART_HandleTypeDef huart4;
UART_HandleTypeDef huart1;
UART_HandleTypeDef huart2;
UART_HandleTypeDef huart3;

/* USER CODE BEGIN PV */
ADC_HandleTypeDef hadc1;        // ADC 控制句柄
//ADC_HandleTypeDef hadc2;
I2C_HandleTypeDef hi2c1;        // I2C 控制句柄
UART_HandleTypeDef huart1;      // UART1 控制句柄
UART_HandleTypeDef huart2;      // UART2 控制句柄
UART_HandleTypeDef huart3;
int i = 0;
int state=0;
int buffer[WINDOW_SIZE] = {0};
int index = 0;
int count = 0;
int x=0;
uint8_t ledTrigger = 0;
uint32_t lastDebounceTime = 0;
typedef enum {
    FSR_RELEASED = 0,
	FSR_PRESSED = 1
} FSR_State;
FSR_State fsrState = FSR_RELEASED;


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

//
ADCReadContext_t fsr1Context = {0};
ADCReadContext_t fsr2Context = {0};


//


//int fsrValueGlobal=0;
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
void PeriphCommonClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_ADC1_Init(void);
static void MX_I2C1_Init(void);
static void MX_USART1_UART_Init(void);
static void MX_USART2_UART_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_UART4_Init(void);
static void MX_ADC2_Init(void);
/* USER CODE BEGIN PFP */
void SystemClock_Config(void);
//void transmit_data_uart(char* bufferPtr);
//void ReceiveData();
//void transmit_data_uart(void);
//void receive_data_uart(void);


/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
/* 重定向 printf 到 UART */


void example(int arr[]) {
    int ww=sizeof(arr);  // ❌ 這裡不是陣列大小 w=4
}
void lightOnLED(void)
{
	//int count=0;
	//int statusLED=0;
	//HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
    //state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);
    //HAL_Delay(100);
}
void lightOffLED(void)
{
	//int count=0;
	//int statusLED=0;

    //將 PB8 Off
    //HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
    //state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);
    //receive_data_uart();
    //HAL_Delay(100);
    //i++;
}
//讀取多次平均 + 無阻塞延遲
/*
int readAnalogFSR(void)
{
    int samples = 3;
    int sum = 0;
    int adc_value=0;
    for (int i = 0; i < samples; i++) {
        HAL_ADC_Start(&hadc1);
        HAL_ADC_PollForConversion(&hadc1, 10);
        adc_value=HAL_ADC_GetValue(&hadc1);
        sum +=adc_value;
        //sum += HAL_ADC_GetValue(&hadc1);
        HAL_Delay(5);
    }
    return sum / samples;
}*/
void updateFSRState(void)
{
	//char buffer[40]={0};
	char buffer[40] = "234";
	char rxData[10]={0};
	int value=100;
	HAL_StatusTypeDef statusReceive;
	HAL_StatusTypeDef status;
	//int sampleAvgValue = readAveragedFSR(3);  //在同一時間點連續讀多次 ADC，算出平均（多次取樣的平均）,連續讀取 N 次 ADC，算算數平均
	char ch;

	// 讀取經過滑動平均的 FSR 值
	//int slidingAvgValue = getSlidingAverageFSRValue(); //隨著時間對連續多次讀取的值做滑動視窗平均，有記憶之前的 N 筆數據，平滑資料變化
    //int value = readAnalogFSR();

	//value=sampleAvgValue;
	//value=slidingAvgValue;

    uint32_t currentTime = HAL_GetTick();

   // if (fsrState == FSR_RELEASED)
    //{
        if (value > FSR_THRESHOLD_PRESS)
        {
            if ((currentTime - lastDebounceTime) > DEBOUNCE_DELAY_MS)
            {
            	fsrState = FSR_PRESSED;
                lastDebounceTime = currentTime;
                //lightOnLED();
                //value=954;
                //snprintf(buffer, sizeof(buffer), "%d", value);

                //transmitDataUart(buffer);
                //HAL_Delay(1000);
                // 接收剛剛送出的 3 個字元
                //HAL_UART_Receive(&huart1, (uint8_t*)rx, 3, 1000);
                //statusReceive = HAL_UART_Receive(&huart3, (uint8_t*)rxData, 2, 10000);
                //////////////////
                //char rxData[3] = {0}; // 多一個位元放 \0 做字串結尾
                //HAL_StatusTypeDef statusReceive;
                //statusReceive = HAL_UART_Receive(&huart3, (uint8_t*)rxData, 2, 10000);//huart2
                /////////
                //while (i < sizeof(rxData) - 1)
			    //{
				///
                status=HAL_UART_Transmit(&huart3, (uint8_t*)"11223", 5, 1000);
                HAL_Delay(50); // 增加這個 delay，再進行接收會比較穩

                i=0;
                while (i < 5) {
                    statusReceive = HAL_UART_Receive(&huart3, (uint8_t*)&ch, 1, 20000);//&huart2
                    if (statusReceive == HAL_OK) {
                        rxData[i] = ch;
                        printf("Got char: %c\n", ch);
                        i++;
                    } else {
                        printf("Timeout or error at %d chars\n", i);
                        break;
                    }
                }
                rxData[i];
                ///////////////////////////////////////
                /*
                for(int i=0;i<3;)
                    {
						//statusReceive = HAL_UART_Receive(&huart3, (uint8_t*)&ch, 1, 15000);
						statusReceive = HAL_UART_Receive(&huart3, (uint8_t*)rxData, 3, 5000);
						if (statusReceive == HAL_OK)
						{
							rxData[i] = ch;
							i++;
						}
						else
						{
							break; // 超時就退出
						}
                    }*/

			    //}
               // rxData[i] = '\0';

                ////////
                //char ch;
                //HAL_StatusTypeDef status = HAL_UART_Receive(&huart3, (uint8_t*)&ch, 1, 10000);

                if (statusReceive == HAL_OK)
                {
                    printf("Received: %s\n", rxData);
                }
                else if (statusReceive == HAL_TIMEOUT)
                {
                    printf("Receive timeout.\n");
                }
                else
                {
                    printf("Receive error.\n");
                }
                //
                //receiveDataUart();
                int b=33;

                // 這裡可以觸發按下事件
            }
        }
        else
        {
            lastDebounceTime = currentTime;
            lightOffLED();//暫時加上
        }
    //}
    /*else
    {
        if (value < FSR_THRESHOLD_RELEASE)
        {
            if ((currentTime - lastDebounceTime) > DEBOUNCE_DELAY_MS)
            {
                fsrState = FSR_RELEASED;
                lastDebounceTime = currentTime;
                // 這裡可以觸發放開事件
                lightOffLED();
            }
        }
        else
        {
            lastDebounceTime = currentTime;
        }
    }*/

}
int getSlidingAverageFSRValue(void)
{
    //int raw = readSingleADCValue();
    //int slidingAvg = slidingWindowAvg(raw);
    //return slidingAvg;
}
void receiveDataUart()
{
	/*
	char rxData[10] = {0};
	HAL_StatusTypeDef statusReceive;
	statusReceive = HAL_UART_Receive(&huart3, (uint8_t*)rxData, 1, 5000);
    if (statusReceive == HAL_OK)
    {
    	lightOnLED();
	    // 成功收到資料
	    printf("Received: %s\n", rxData);
    } else {
	    // 接收失敗或超時
	    printf("Receive timeout or error\n");
    }
    */
    ///
	char rxData[10] = {0};
    char ch;
    int i = 0;
    HAL_StatusTypeDef statusReceive;
    while (i < sizeof(rxData) - 1)
    {
    	///
    	statusReceive = HAL_UART_Receive(&huart1, (uint8_t*)&ch, 1, 6000);
		if (statusReceive == HAL_OK)
		{
			rxData[i++] = ch;
		}
		else
		{
			break; // 超時就退出
		}

    }
  rxData[i] = '\0';
  //printf("Received: %s\n", rxData);  // 應該會看到 654␍␊
    ////
}
void transmitDataUart(char* bufferPtr)
{
	HAL_StatusTypeDef statustransmit;
	int a=strlen(bufferPtr);
	//HAL_UART_Transmit(&huart2, (uint8_t*)msg, strlen(msg), HAL_MAX_DELAY);
	statustransmit=HAL_UART_Transmit(&huart1, (uint8_t*)bufferPtr, strlen(bufferPtr), 1000);//&huart2

}
int slidingWindowAvg(int new_sample) {

    buffer[index] = new_sample;
    index = (index + 1) % WINDOW_SIZE;
    if (count < WINDOW_SIZE) count++;

    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += buffer[i];
    }

    return sum / count;
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
  /* Prevent unused argument(s) compilation warning */
	if(GPIO_Pin == GPIO_PIN_13){
		ledTrigger = 1;
		HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
		//HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_8);  // 切換燈狀態
	    //HAL_Delay(200);
	    //將 PB8 Off
	    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
		//x = (x == 0)? 1:0;
	}
}

//
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


////////



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
	}

	return allForceSensorStateResult;



	//////////
	/*
	bool allForceSensorStateResult=false;
	uint32_t forceSensor1AveragedaValue=0;
	uint32_t forceSensor2AveragedaValue=0;
	bool fsr1Done = false;
	bool fsr2Done = false;
	uint32_t fsr1Value = 0;
	uint32_t fsr2Value = 0;

	if (isSensor1Enabled && isSensor2Enabled)
	{
		//非阻塞
		startADCRead(&fsr1Context, 1, sensorPressDuration);
		startADCRead(&fsr2Context, 2, sensorPressDuration);
		fsr1Done = false;
		fsr2Done = false;
		while (1)
		{
				// 可在這裡執行其他任務，非阻塞


			if (!fsr1Done && processADCRead(&fsr1Context)) {
				forceSensor1AveragedaValue = getADCReadAverage(&fsr1Context);
				fsr1Done = true;
				//printf("FSR1 average = %lu\n", fsr1Value);
			}

			if (!fsr2Done && processADCRead(&fsr2Context)) {
				forceSensor2AveragedaValue = getADCReadAverage(&fsr2Context);
				fsr2Done = true;
				printf("FSR2 average = %lu\n", fsr2Value);
			}

			// 當兩個都完成後處理資料
			if (fsr1Done && fsr2Done)
			{
				if(forceSensor1AveragedaValue > pressureValueThreshold ||forceSensor2AveragedaValue > pressureValueThreshold)
				{
					allForceSensorStateResult=true;
				}
				break;
				//printf("FSR1 = %lu, FSR2 = %lu\n", fsr1Value, fsr2Value);
			}
		}


		/////////////////////
		//forceSensor1AveragedaValue=readAveragedFSR(1,sensorPressDuration);//讀完forceSensor1AveragedaValue才會往下走
		//forceSensor2AveragedaValue=readAveragedFSR(2,sensorPressDuration);//
		//if(forceSensor1AveragedaValue > pressureValueThreshold ||forceSensor2AveragedaValue > pressureValueThreshold)
		//{
			//allForceSensorStateResult=true;
		//}
	     //return true; // 兩個sensor都沒啟用，回傳 false
	}
	else if(isSensor1Enabled)
	{
		forceSensor1AveragedaValue=readAveragedFSR(1,sensorPressDuration);
		if(forceSensor1AveragedaValue > pressureValueThreshold)
		{
			allForceSensorStateResult=true;
		}

	}
	else if(isSensor2Enabled)
	{
		forceSensor2AveragedaValue=readAveragedFSR(2,sensorPressDuration);//再改成2
				if(forceSensor2AveragedaValue > pressureValueThreshold)
				{
					allForceSensorStateResult=true;
				}

	}
	else
	{
		allForceSensorStateResult=false;
	}
	return allForceSensorStateResult;
	*/
}









////////////////////

bool checkSwitchState(int sensorIndex,uint32_t switchDebounceDuration)
{
	bool isTouchSwitchPressed=false;
	uint32_t static lastDebounceTime = 0;//它只會在程式執行到該行定義時 初始化一次（第一次呼叫函數時）。
    //之後每次呼叫 checkSwitchState() 時，這個變數都會保留上一次的值，不會再被重設為 0
    static GPIO_PinState lastButtonState = GPIO_PIN_SET;//沒按下 PC8 透過電阻拉到 3.3V（邏輯高
	GPIO_PinState currentState = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);//低電位
	if (currentState != lastButtonState)
	{
		lastDebounceTime = HAL_GetTick();  // 有變化就重設時間
	}
	uint32_t elapsed = HAL_GetTick() - lastDebounceTime;  // 算出經過了多少毫秒
	if (elapsed > switchDebounceDuration)
	{
		if (currentState == GPIO_PIN_RESET)
		{
			// 按鈕已穩定按下，可以執行動作
			isTouchSwitchPressed=true;

		}
	}

	lastButtonState = currentState;
}
bool getAllTouchSwitchState(bool isSwitch1Enabled,bool isSwitch2Enabled,bool isSwitch3Enabled,bool isSwitch4Enabled,uint32_t touchSwitchDebounceDuration)
{
	bool allTouchSwitchStateResult=false;
	//bool isTouchSwitch1Pressed = true;  // 開關1被按下
	bool isTouchSwitch1Pressed = false; // 開關1沒被按下
	bool isTouchSwitch2Pressed = false;
	bool isTouchSwitch3Pressed = false;
	bool isTouchSwitch4Pressed = false;
	uint32_t forceSensor2AveragedaValue=0;
	int disabledCount = 0;
	if (!isSwitch1Enabled) disabledCount++;
	if (!isSwitch2Enabled) disabledCount++;
	if (!isSwitch3Enabled) disabledCount++;
	if (!isSwitch4Enabled) disabledCount++;

	if (disabledCount == 0)
	{   //四個開關都啟用
		isTouchSwitch1Pressed=checkSwitchState(1,touchSwitchDebounceDuration);
		isTouchSwitch2Pressed=checkSwitchState(2,touchSwitchDebounceDuration);//再改成2

		int pressedCount = isTouchSwitch1Pressed + isTouchSwitch2Pressed + isTouchSwitch3Pressed + isTouchSwitch4Pressed;
		if (pressedCount >= 2) {
		    // 執行事情
		}
		else
		{
		    // 開關1沒被按下要做的事
		}
		//forceSensor1AveragedaValue=0;
		//forceSensor2AveragedaValue=0;
		//if(forceSensor1AveragedaValue > pressureValueThreshold ||forceSensor2AveragedaValue > pressureValueThreshold)
		//{
			//allForceSensorStateResult=true;
		//}
		 //return true; // 兩個sensor都沒啟用，回傳 false

	}
	else if (disabledCount == 1)
	{
		printf("一個 switch 不啟用\n");
		printf("啟用的 switch 有：");
		if (isSwitch1Enabled) printf("Switch1 ");

	}
	else if (disabledCount == 2)
	{
		printf("兩個 switch 不啟用\n");
		printf("啟用的 switch 有：");
		if (isSwitch1Enabled) printf("Switch1 ");
		if (isSwitch2Enabled) printf("Switch2 ");
		if (isSwitch3Enabled) printf("Switch3 ");
		if (isSwitch4Enabled) printf("Switch4 ");

	}
	else if (disabledCount == 3) {
		printf("三個 switch 不啟用\n");
		printf("啟用的 switch 有：");
		if (isSwitch1Enabled) printf("Switch1 ");
		if (isSwitch2Enabled) printf("Switch2 ");
		if (isSwitch3Enabled) printf("Switch3 ");
		if (isSwitch4Enabled) printf("Switch4 ");

	}
	else if (disabledCount == 4) {
		printf("全部 switch 都不啟用\n");
	}
	else {
		printf("狀況不明\n");
	}
	return allTouchSwitchStateResult;
}



/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */
  //char buffer[40]="";
  int arr[10] = {0};  // 全部初始化為 0
  int a=sizeof(arr);  // ✅ 這裡是陣列大小  a=40   10*4
  int value=2;

  //example(arr);

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* Configure the peripherals common clocks */
  PeriphCommonClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_ADC1_Init();
  MX_I2C1_Init();
  MX_USART1_UART_Init();
  MX_USART2_UART_Init();
  MX_USART3_UART_Init();
  MX_UART4_Init();
  MX_ADC2_Init();
  /* USER CODE BEGIN 2 */


  /*if (HAL_UART_Transmit(&huart1, txData, sizeof(txData), 1000) != HAL_OK) {
  Error_Handler();  // 發送錯誤處理
  }*/

  // 接收數據
 // uint8_t rxData[10];
  //if (HAL_UART_Receive(&huart1, rxData, sizeof(rxData), 1000) != HAL_OK) {
  //Error_Handler();  // 接收錯誤處理
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
	  // 全部力量感測器回傳值
	  bool forceSensorFinalState=false;
	  //從flash讀取力量感測器初始參數
	  uint32_t forceSensorPressDuration = 100;
	  uint32_t forcepPressValueThreshold = 3000; //
	  bool isforceSensor1Enabled=true;
	  bool isforceSensor2Enabled=true;
	  //

	  // Touch switch enabled flags
	  bool isTouchSwitch1Enabled = true;
	  bool isTouchSwitch2Enabled = true;
	  bool isTouchSwitch3Enabled = true;
	  bool isTouchSwitch4Enabled = true;

	  // Touch switch behavior parameters
	  uint32_t touchSwitchDebounceDuration = 100;
	  uint32_t touchSwitchPressThreshold = 3000;

	  // Final result of all switches
	  bool touchSwitchFinalState = false;

	  //
	  uint32_t startTime = HAL_GetTick();
	  forceSensorFinalState=getAllForceSensorState(isforceSensor1Enabled,isforceSensor2Enabled,forceSensorPressDuration,forcepPressValueThreshold);


	  uint32_t endTime = HAL_GetTick();
	  uint32_t duration = endTime - startTime;






	  touchSwitchFinalState = getAllTouchSwitchState(
	      isTouchSwitch1Enabled,
	      isTouchSwitch2Enabled,
	      isTouchSwitch3Enabled,
	      isTouchSwitch4Enabled,
	      touchSwitchDebounceDuration);
	  //

	  /*
	  if (ledTrigger) {
	          HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
	          HAL_Delay(5000);
	          HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
	          ledTrigger = 0;
	      }
	      */
	  //

	  //HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);

	  //HAL_Delay(200);
	  //將 PB8 Off
	  //HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);
	  //uint32_t sensor1Flag=0;
	  //uint32_t sensor2Flag=0;


	  //getAllTouchSwitchState();



	  ///
	  ///
	  //snprintf(buffer, sizeof(buffer), "%d", value);
	  //transmitDataUart(buffer);

	  //
	  char txData[] = "12345";
	  //char rxData[10] = "0";
	  //char rxData[10] = { '0','0','0','0','0','0','0','0','0','0' };
	  HAL_StatusTypeDef status_transmit;
	  HAL_StatusTypeDef status;
	  /////////////
	  //uint8_t tx = 'H';
	  //uint8_t rx = 0;
	  //HAL_Delay(2000);
	  //status=HAL_UART_Receive(&huart2, &rx, 1, 3000);//PA3
	  //status_transmit=HAL_UART_Transmit(&huart2, &rx, 1, 1000);
	  /*
	  uint8_t tx = 'HWQ';
	  uint8_t rx = 0;

	  status_transmit=HAL_UART_Transmit(&huart2, &txData, 3, 1000);  // UART1 TX（例如 PA9）
	  HAL_Delay(5000);
	  ///

	  char rxData[10] = {0};
	  char ch;
	  int i = 0;

	  while (i < sizeof(rxData) - 1)
	  {
		  status=HAL_UART_Receive(&huart2, (uint8_t*)&ch, 1, 3000) ;
	      if (status == HAL_OK)
	      {
	          rxData[i++] = ch;
	          if (ch == '\n') break;  // 遇到換行結束
	      }
	      else
	      {
	          printf("Timeout\n");
	          break;
	      }
	  }
	  rxData[i] = '\0';
	  printf("Received: %s\n", rxData);  // 應該會看到 654␍␊


	  ///
	  //status = HAL_UART_Receive(&huart2, &rxData, 2, 3000); // UART3 RX（PC5）

	  if (status == HAL_OK && rx == 'H') {
	      HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_8); // 收到正確資料就閃燈
	  }
	  */
	  //
	  //status_transmit=HAL_UART_Transmit(&huart2, &tx, 1, 1000);
	  //HAL_Delay(1000);
	  //status=HAL_UART_Receive(&huart2, &rx, 1, 3000);//PA3
	  //if (status == HAL_OK) {
	    //  if (rx == 'H') {
	      //    HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_8);  // 有收到正確資料就閃燈
	      //}
	  //}
	  ///////////////
/*
	  status_transmit = HAL_UART_Transmit(&huart2, (uint8_t*)txData, strlen(txData), 1000);
	  if (status != HAL_OK) {
		  //將 PB8 On起來
		  	  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_SET);
		  	  state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);  //平常開關 沒按下 PC8 透過電阻拉到 3.3V（邏輯高，GPIO_PIN_SET
		  	  i--;
		  	  //transmit_data_uart();
		  	  HAL_Delay(200);
		  	  //將 PB8 Off
		  	  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_8, GPIO_PIN_RESET);//開關 按下時： PC8 直接接地 → 邏輯低 (GPIO_PIN_RESET)
		  	  state = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_8);
		  	  //receive_data_uart();
		  	  HAL_Delay(200);
		  	  i++;
	      // 錯誤處理
	  }//uart2 才能用 虛擬 port 收發資料
	  // 接上 USB後  UART2 就會被電腦佔走,所以 UART2  TX RX 都不能用


	  status = HAL_UART_Receive(&huart2, (uint8_t*)rxData, 5, 5000);
	  if (status == HAL_OK) {
	      // 成功收到資料
	      printf("Received: %s\n", rxData);
	  } else {
	      // 接收失敗或超時
	      printf("Receive timeout or error\n");
	  }
*/
	  // 啟用力量感測器功能
	  //updateFSRState();   // 呼叫防彈跳判斷
	  HAL_Delay(100);     // 簡短延遲避免過度讀取ADC
	  //
	  //printf("Tick\r\n");
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
	 // printf("Hello, jjjjjjjjjjjjjjjSTM32!\r\n");

	  //讀取類比資料adc
	  //fsrValueGlobal=readAnalogFSR();
	 // if(fsrValueGlobal>3500)
	  //{
		//  lightOnLED();
	 // }
	  //else
	  //{
	//	  fsrValueGlobal=0;
	  //}
	  //HAL_ADC_Start(&hadc1);
	  //HAL_ADC_PollForConversion(&hadc1,1);
	  //value = HAL_ADC_GetValue(&hadc1);
	  // 使用 snprintf 安全地將整數轉換為字串
	  //snprintf(buffer, sizeof(buffer), "%d", value);
	  //snprintf(buffer, sizeof(buffer), "fsr讀到的數值是: %d", value);

	  //transmit_data_uart(buffer);
	  //HAL_Delay(10);
	  //ReceiveData();
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  if (HAL_PWREx_ControlVoltageScaling(PWR_REGULATOR_VOLTAGE_SCALE1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 1;
  RCC_OscInitStruct.PLL.PLLN = 10;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV7;
  RCC_OscInitStruct.PLL.PLLQ = RCC_PLLQ_DIV2;
  RCC_OscInitStruct.PLL.PLLR = RCC_PLLR_DIV2;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_4) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief Peripherals Common Clock Configuration
  * @retval None
  */
void PeriphCommonClock_Config(void)
{
  RCC_PeriphCLKInitTypeDef PeriphClkInit = {0};

  /** Initializes the peripherals clock
  */
  PeriphClkInit.PeriphClockSelection = RCC_PERIPHCLK_ADC;
  PeriphClkInit.AdcClockSelection = RCC_ADCCLKSOURCE_PLLSAI1;
  PeriphClkInit.PLLSAI1.PLLSAI1Source = RCC_PLLSOURCE_HSI;
  PeriphClkInit.PLLSAI1.PLLSAI1M = 1;
  PeriphClkInit.PLLSAI1.PLLSAI1N = 8;
  PeriphClkInit.PLLSAI1.PLLSAI1P = RCC_PLLP_DIV7;
  PeriphClkInit.PLLSAI1.PLLSAI1Q = RCC_PLLQ_DIV2;
  PeriphClkInit.PLLSAI1.PLLSAI1R = RCC_PLLR_DIV2;
  PeriphClkInit.PLLSAI1.PLLSAI1ClockOut = RCC_PLLSAI1_ADC1CLK;
  if (HAL_RCCEx_PeriphCLKConfig(&PeriphClkInit) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief ADC1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC1_Init(void)
{

  /* USER CODE BEGIN ADC1_Init 0 */

  /* USER CODE END ADC1_Init 0 */

  ADC_MultiModeTypeDef multimode = {0};
  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC1_Init 1 */

  /* USER CODE END ADC1_Init 1 */

  /** Common config
  */
  hadc1.Instance = ADC1;
  hadc1.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc1.Init.Resolution = ADC_RESOLUTION_12B;
  hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc1.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc1.Init.LowPowerAutoWait = DISABLE;
  hadc1.Init.ContinuousConvMode = DISABLE;
  hadc1.Init.NbrOfConversion = 1;
  hadc1.Init.DiscontinuousConvMode = DISABLE;
  hadc1.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc1.Init.DMAContinuousRequests = DISABLE;
  hadc1.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc1.Init.OversamplingMode = DISABLE;
  if (HAL_ADC_Init(&hadc1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure the ADC multi-mode
  */
  multimode.Mode = ADC_MODE_INDEPENDENT;
  if (HAL_ADCEx_MultiModeConfigChannel(&hadc1, &multimode) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_1;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_2CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC1_Init 2 */

  /* USER CODE END ADC1_Init 2 */

}

/**
  * @brief ADC2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_ADC2_Init(void)
{

  /* USER CODE BEGIN ADC2_Init 0 */

  /* USER CODE END ADC2_Init 0 */

  ADC_ChannelConfTypeDef sConfig = {0};

  /* USER CODE BEGIN ADC2_Init 1 */

  /* USER CODE END ADC2_Init 1 */

  /** Common config
  */
  hadc2.Instance = ADC2;
  hadc2.Init.ClockPrescaler = ADC_CLOCK_ASYNC_DIV1;
  hadc2.Init.Resolution = ADC_RESOLUTION_12B;
  hadc2.Init.DataAlign = ADC_DATAALIGN_RIGHT;
  hadc2.Init.ScanConvMode = ADC_SCAN_DISABLE;
  hadc2.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
  hadc2.Init.LowPowerAutoWait = DISABLE;
  hadc2.Init.ContinuousConvMode = DISABLE;
  hadc2.Init.NbrOfConversion = 1;
  hadc2.Init.DiscontinuousConvMode = DISABLE;
  hadc2.Init.ExternalTrigConv = ADC_SOFTWARE_START;
  hadc2.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
  hadc2.Init.DMAContinuousRequests = DISABLE;
  hadc2.Init.Overrun = ADC_OVR_DATA_PRESERVED;
  hadc2.Init.OversamplingMode = DISABLE;
  if (HAL_ADC_Init(&hadc2) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Regular Channel
  */
  sConfig.Channel = ADC_CHANNEL_2;
  sConfig.Rank = ADC_REGULAR_RANK_1;
  sConfig.SamplingTime = ADC_SAMPLETIME_2CYCLES_5;
  sConfig.SingleDiff = ADC_SINGLE_ENDED;
  sConfig.OffsetNumber = ADC_OFFSET_NONE;
  sConfig.Offset = 0;
  if (HAL_ADC_ConfigChannel(&hadc2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN ADC2_Init 2 */

  /* USER CODE END ADC2_Init 2 */

}

/**
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.Timing = 0x10D19CE4;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.OwnAddress2Masks = I2C_OA2_NOMASK;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Analogue filter
  */
  if (HAL_I2CEx_ConfigAnalogFilter(&hi2c1, I2C_ANALOGFILTER_ENABLE) != HAL_OK)
  {
    Error_Handler();
  }

  /** Configure Digital filter
  */
  if (HAL_I2CEx_ConfigDigitalFilter(&hi2c1, 0) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

}

/**
  * @brief UART4 Initialization Function
  * @param None
  * @retval None
  */
static void MX_UART4_Init(void)
{

  /* USER CODE BEGIN UART4_Init 0 */

  /* USER CODE END UART4_Init 0 */

  /* USER CODE BEGIN UART4_Init 1 */

  /* USER CODE END UART4_Init 1 */
  huart4.Instance = UART4;
  huart4.Init.BaudRate = 115200;
  huart4.Init.WordLength = UART_WORDLENGTH_8B;
  huart4.Init.StopBits = UART_STOPBITS_1;
  huart4.Init.Parity = UART_PARITY_NONE;
  huart4.Init.Mode = UART_MODE_TX_RX;
  huart4.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart4.Init.OverSampling = UART_OVERSAMPLING_16;
  huart4.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart4.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart4) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN UART4_Init 2 */

  /* USER CODE END UART4_Init 2 */

}

/**
  * @brief USART1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART1_UART_Init(void)
{

  /* USER CODE BEGIN USART1_Init 0 */

  /* USER CODE END USART1_Init 0 */

  /* USER CODE BEGIN USART1_Init 1 */

  /* USER CODE END USART1_Init 1 */
  huart1.Instance = USART1;
  huart1.Init.BaudRate = 115200;
  huart1.Init.WordLength = UART_WORDLENGTH_8B;
  huart1.Init.StopBits = UART_STOPBITS_1;
  huart1.Init.Parity = UART_PARITY_NONE;
  huart1.Init.Mode = UART_MODE_TX_RX;
  huart1.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart1.Init.OverSampling = UART_OVERSAMPLING_16;
  huart1.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart1.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART1_Init 2 */

  /* USER CODE END USART1_Init 2 */

}

/**
  * @brief USART2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART2_UART_Init(void)
{

  /* USER CODE BEGIN USART2_Init 0 */

  /* USER CODE END USART2_Init 0 */

  /* USER CODE BEGIN USART2_Init 1 */

  /* USER CODE END USART2_Init 1 */
  huart2.Instance = USART2;
  huart2.Init.BaudRate = 115200;
  huart2.Init.WordLength = UART_WORDLENGTH_8B;
  huart2.Init.StopBits = UART_STOPBITS_1;
  huart2.Init.Parity = UART_PARITY_NONE;
  huart2.Init.Mode = UART_MODE_TX_RX;
  huart2.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart2.Init.OverSampling = UART_OVERSAMPLING_16;
  huart2.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart2.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart2) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART2_Init 2 */

  /* USER CODE END USART2_Init 2 */

}

/**
  * @brief USART3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  huart3.Init.OneBitSampling = UART_ONE_BIT_SAMPLE_DISABLE;
  huart3.AdvancedInit.AdvFeatureInit = UART_ADVFEATURE_NO_INIT;
  if (HAL_UART_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */

  /* USER CODE END USART3_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
  /* USER CODE BEGIN MX_GPIO_Init_1 */

  /* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOH_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(LD2_GPIO_Port, LD2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0|GPIO_PIN_14|GPIO_PIN_7|GPIO_PIN_8, GPIO_PIN_RESET);

  /*Configure GPIO pin : PC13 */
  GPIO_InitStruct.Pin = GPIO_PIN_13;
  GPIO_InitStruct.Mode = GPIO_MODE_IT_RISING;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /*Configure GPIO pin : LD2_Pin */
  GPIO_InitStruct.Pin = LD2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(LD2_GPIO_Port, &GPIO_InitStruct);

  /*Configure GPIO pins : PB0 PB14 PB7 PB8 */
  GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_14|GPIO_PIN_7|GPIO_PIN_8;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pin : PC8 */
  GPIO_InitStruct.Pin = GPIO_PIN_8;
  GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

  /* EXTI interrupt init*/
  HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
  HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);

  /* USER CODE BEGIN MX_GPIO_Init_2 */

  /* USER CODE END MX_GPIO_Init_2 */
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
