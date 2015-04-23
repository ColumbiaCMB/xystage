/* Based on https://github.com/MotorDriver/L6474/blob/master/L6474SketchFor1MotorShieldDrivenByUart/L6474SketchFor1MotorShieldDrivenByUart.ino */

#include <l6474_target_config.h>


#include <l6474.h>
#include <SPI.h>

#define NB_L6474_UART_COMMAND (36)

const uint8_t aCommandArgumentNb[NB_L6474_UART_COMMAND] = {0 ,   //C1 GetAcceleration
                                                           0,    //C2 GetCurrentSpeed
                                                           0,    //C3 GetDeceleration
                                                           0,    //C4 GetShieldState                                                           
                                                           0,    //C5 GetFwVersion
                                                           0,    //C6 GetMark
                                                           0,    //C7 GetMaxSpeed
                                                           0,    //C8 GetMinSpeed
                                                           0,    //C9 GetPosition
                                                           0,    //C10 GoHome
                                                           0,    //C11 GoMark
                                                           1,    //C12 GoTo
                                                           0,    //C13 HardStop
                                                           2,    //C14 Move
                                                           0,    //C15 ResetAllShields
                                                           1,    //C16 Run
                                                           1,    //C17 SetAcceleration
                                                           1,    //C18 SetDeceleration
                                                           0,    //C19 SetHome
                                                           0,    //C20 SetMark
                                                           1,    //C21 SetMaxSpeed
                                                           1,    //C22 SetMinSpeed
                                                           0,    //C23 SoftStop
                                                           0,    //C24 WaitWhileActive
                                                           0,    //C25 CmdDisable
                                                           0,    //C26 CmdEnable
                                                           1,    //C27 CmdGetParam
                                                           0,    //C28 CmdGetStatus
                                                           0,    //C29 CmdNop
                                                           2,    //C30 CmdSetParam
                                                           0,    //C31 ReadStatusRegister
                                                           0,    //C32 Reset
                                                           0,    //C33 ReleaseReset
                                                           1,    //C34 SelectStepMode
                                                           1};   //C35 SetDirection
                                                           
L6474 myL6474;  

uint8_t gParserState = 0;
uint8_t gCommand = 0;
uint32_t gArg1 = 0;
uint32_t gArg2 = 0;
uint32_t gTarget = 0;

void setup()
{
  uint16_t mySpeed;

//----- Init

  // initialize serial:
  Serial.begin(9600);
  Serial.setTimeout(10000);

  /* Start the library to use 2 shields */
  /* The L6474 registers are set with the predefined values */
  /* from file l6474_target_config.h*/
  myL6474.Begin(2);

  /* Attach the function MyFlagInterruptHandler (defined below) to the flag interrupt */
  myL6474.AttachFlagInterrupt(MyFlagInterruptHandler);
  
  Serial.print(">");        
}

void loop()
{
 static  char newInputChar;

  while (Serial.available() > 0) 
  {
    newInputChar = Serial.read();

    if ((gParserState == 0) && 
        (newInputChar != '\n') &&
        (newInputChar != '\r') &&        
        (newInputChar != ' '))
    {
      ParseCommand(newInputChar);
    }
    else if ((gParserState ==1)&&
             (newInputChar == '\n'))
    {
      //Serial.print("Ok: found Command C");
      Serial.print("C");
      Serial.print(gCommand, DEC);
      Serial.print(" ");
      //Serial.print(" for target = ");
      Serial.print(gTarget, DEC);
      if (aCommandArgumentNb[gCommand - 1] > 0)
      {
        //Serial.print(" with argument1 = ");
        Serial.print(" ");
        Serial.print(gArg1, DEC);
      }
      if (aCommandArgumentNb[gCommand - 1] > 1)
      {
        //Serial.print(" and argument2 = ");
        Serial.print(" ");
        Serial.print(gArg2, DEC);
      }      
      Serial.println();      

      // Execute command
      ExecuteCommand(gCommand, gTarget, gArg1, gArg2);
      gParserState = 0; 
      Serial.print(">");        
    }
  }
}

void ParseCommand(char newChar)
{
  uint8_t foundCommand = 0;
  if (gParserState == 0)
  {
    if (newChar == 'C')
    {
      uint8_t newCommand;
      
      gCommand = Serial.parseInt();
      
      if ((gCommand != 0) && (gCommand <= NB_L6474_UART_COMMAND))
      {
        gTarget = Serial.parseInt();
        if (gTarget > 1) {
          gTarget = 0;
        }
        if (aCommandArgumentNb[gCommand - 1] > 0)
        {
          gArg1 = Serial.parseInt();
        }
        if (aCommandArgumentNb[gCommand - 1] > 1)
        {
          gArg2 = Serial.parseInt();
        }
        gParserState = 1;
      }
      else
      {
        Serial.print("Error: ");
        //Serial.print("\nError: unknown command -> must be between C1 and C");
        Serial.println(NB_L6474_UART_COMMAND, DEC);
        Serial.print(">");   
      }
    }
    else
    {
      //Serial.println("Error: command must start by C");
      Serial.print("Error");
      Serial.print(">");              
    }
  }
}

void ExecuteCommand (uint8_t newCommand, uint32_t target, uint32_t newArg1, uint32_t newArg2)
{
  dir_t newDirection;
  uint32_t data; 
  switch (newCommand)
  {
     case 1:
       //C1 GetAcceleration
       data = myL6474.GetAcceleration(target);
//       Serial.print("Acceleration : ");
       Serial.print("R ");
       Serial.println(data, DEC);     
       break;
     case 2:
      //C2 GetCurrentSpeed
       data = myL6474.GetCurrentSpeed(target);
//       Serial.print("Current speed : ");
       Serial.print("R ");
       Serial.println(data, DEC);     
      break;  
     case 3:
      //C3 GetDeceleration
       data = myL6474.GetDeceleration(target);
//       Serial.print("Current deceleration : ");
       Serial.print("R ");
       Serial.println(data, DEC);           
      break;
     case 4:
      //C4 GetShieldState
       data = myL6474.GetShieldState(target);
//       Serial.print("Current state : ");
       Serial.print("R ");
       Serial.println(data, DEC);           
      break;
     case 5:
      //C5 GetFwVersion
       data = myL6474.GetFwVersion();
//       Serial.print("FW version : ");
       Serial.print("R ");
       Serial.println(data, DEC);          
      break;
     case 6:
      //C6 GetMark
       data = myL6474.GetMark(target);
//       Serial.print("Mark : ");
       Serial.print("R ");
       Serial.println(data, DEC);      
      break;
     case 7:
      //C7 GetMaxSpeed
       data = myL6474.GetMaxSpeed(target);
//       Serial.print("Max Speed : ");
       Serial.print("R ");
       Serial.println(data, DEC);        
      break;
     case 8:
      //C8 GetMinSpeed
       data = myL6474.GetMinSpeed(target);
//       Serial.print("Min Speed : ");
       Serial.print("R ");
       Serial.println(data, DEC);            
      break;
     case 9:
       //C9 GetPosition
       data = myL6474.GetPosition(target);
//       Serial.print("Current position: ");
       Serial.print("R ");
       Serial.println(data, DEC);       
      break;
     case 10:
      //C10 GoHome
       myL6474.GoHome(target);
//       Serial.println("Executing go home");      
      break;
     case 11:
      //C11 GoMark
       myL6474.GoMark(target);
//       Serial.println("Executing go mark");            
      break;
     case 12:
      //C12 GoTo
       myL6474.GoTo(target, newArg1);
//       Serial.print("Executing go to position: ");
//       Serial.println(newArg1, DEC);      
      break;
     case 13:
      //C13 HardStop
       myL6474.HardStop(target);
//       Serial.print("Hard stop");
      break;
     case 14:
      //C14 Move
      if (newArg1 == 0)
      {
        newDirection = FORWARD;
 //       Serial.print("Executing a forward move command of");
      }
      else
      {
        newDirection = BACKWARD;
 //       Serial.print("Executing a backward move command of");
      }      
       myL6474.Run(target, newDirection);      
       myL6474.Move(target, newDirection, newArg2);
//       Serial.print(newArg1, DEC);
//       Serial.println(" steps");      
      break;
     case 15:
      //C15 ResetAllShields
       myL6474.ResetAllShields();
//       Serial.print("Reset All Shields");
      break;
     case 16:
      //C16 Run
      if (newArg1 == 0)
      {
        newDirection = FORWARD;
 //       Serial.println("Executing a run Command in forward direction");
      }
      else
      {
        newDirection = BACKWARD;
 //       Serial.println("Executing a run Command in backward direction");
      }      
       myL6474.Run(target, newDirection);
       break;               
      break;
     case 17:
       //C17 SetAcceleration
       myL6474.SetAcceleration(target, newArg1);
//       Serial.println("Set acceleration done");               
      break;
     case 18:
      //C18 SetDeceleration
       myL6474.SetDeceleration(target, newArg1);
//       Serial.println("Set deceleration done");        
      break;
     case 19:
      //C19 SetHome
      myL6474.SetHome(target);
      Serial.println("Set home done");      
      break;
     case 20:
      //C20 SetMark
      myL6474.SetMark(target);
      Serial.println("Set mark done");          
      break;      
     case 21:
      //C21 SetMaxSpeed
       myL6474.SetMaxSpeed(target, newArg1);
//       Serial.println("Set max speed done");     
      break;    
     case 22:
      //C22 SetMinSpeed
       myL6474.SetMinSpeed(target, newArg1);
//       Serial.println("Set min speed done");           
      break;    
     case 23:
      //C23 SoftStop
      myL6474.SoftStop(target);
      Serial.println("Soft stop");             
      break;    
     case 24:
      //C24 WaitWhileActive
//      Serial.println("Wait while active ongoing");     
      Serial.println("W");
      myL6474.WaitWhileActive(target);
      Serial.println("R");
//      Serial.println("Wait while active done");       
      break;    
     case 25:
      //C25 CmdDisable
      myL6474.CmdDisable(target);
//      Serial.println("Command Disable done");   
      break;    
     case 26:
      //C26 CmdEnable
      myL6474.CmdEnable(target);
//      Serial.println("Command Enable done");         
      break;    
     case 27:
      //C27 CmdGetParam
       data = myL6474.CmdGetParam(target, (L6474_Registers_t)newArg1);
//       Serial.print("Get param 0x");
       Serial.print("R ");
       Serial.println(data, DEC);   
      
       
      break;    
     case 28:
      //C28 CmdGetStatus
       data = myL6474.CmdGetStatus(target);
//       Serial.print("Get status 0x");
       Serial.print("R ");
       Serial.println(data, DEC);         
      break;    
     case 29:
      //C29 CmdNop
       myL6474.CmdNop(target);
//       Serial.println("Nop command done");      
      break;    
     case 30:
      //C30 CmdSetParam
        myL6474.CmdSetParam(target, (L6474_Registers_t)newArg1, newArg2);
//       Serial.println("Set param done");
      break;          
     case 31:
      //C31 ReadStatusRegister
       data = myL6474.ReadStatusRegister(target);
//       Serial.print("Read status register 0x");
       Serial.print("R ");
       Serial.println(data, DEC);           
      break;    
     case 32:
      //C32 Reset
       myL6474.Reset();
//       Serial.println("Reset done");            
      break;    
     case 33:
      //C33 ReleaseReset
       myL6474.ReleaseReset();
//       Serial.println("Release reset done");            
      break;         
     case 34:
      //C33 SelectStepMode
      L6474_STEP_SEL_t stepMode;
//      Serial.print("Set step mode: ");
      switch (newArg1)
      {
         case 1:
         default:
          stepMode = L6474_STEP_SEL_1;
   //       Serial.println("Full step");
          break;
         case 2:
          stepMode = L6474_STEP_SEL_1_2;
   //       Serial.println("Half step");          
          break;
          case 4:
          stepMode = L6474_STEP_SEL_1_4;
   //       Serial.println("1/4 step");                    
          break;
          case 8:
          stepMode = L6474_STEP_SEL_1_8;
   //       Serial.println("1/8 step");                              
          break;
          case 16:
          stepMode = L6474_STEP_SEL_1_16;
   //       Serial.println("1/16 step");                              
          break;         
      }
      myL6474.SelectStepMode(target, stepMode);   
      break;         
     case 35:
      //C35 SetDirection
      if (newArg1 == 0)
      {
        myL6474.SetDirection(target, FORWARD);     
 //       Serial.println("Set Forward direction");
      }
      else
      {
        myL6474.SetDirection(target, BACKWARD);  
 //       Serial.println("Set Backward direction");
      }      
      break;               
  }
}


void MyFlagInterruptHandler(void)
{
  /* Get the value of the status register via the L6474 command GET_STATUS */
  uint16_t statusRegister = myL6474.CmdGetStatus(0);

  /* Check HIZ flag: if set, power brigdes are disabled */
  if ((statusRegister & L6474_STATUS_HIZ) == L6474_STATUS_HIZ)
  {
    // HIZ state
  }

  /* Check direction bit */
  if ((statusRegister & L6474_STATUS_DIR) == L6474_STATUS_DIR)
  {
    // Forward direction is set
  }  
  else
  {
    // Backward direction is set
  }  

  /* Check NOTPERF_CMD flag: if set, the command received by SPI can't be performed */
  /* This often occures when a command is sent to the L6474 */
  /* while it is in HIZ state */
  if ((statusRegister & L6474_STATUS_NOTPERF_CMD) == L6474_STATUS_NOTPERF_CMD)
  {
       // Command received by SPI can't be performed
  }  

  /* Check WRONG_CMD flag: if set, the command does not exist */
  if ((statusRegister & L6474_STATUS_WRONG_CMD) == L6474_STATUS_WRONG_CMD)
  {
     //command received by SPI does not exist 
  }  

  /* Check UVLO flag: if not set, there is an undervoltage lock-out */
  if ((statusRegister & L6474_STATUS_UVLO) == 0)
  {
     //undervoltage lock-out 
  }  

  /* Check TH_WRN flag: if not set, the thermal warning threshold is reached */
  if ((statusRegister & L6474_STATUS_TH_WRN) == 0)
  {
    //thermal warning threshold is reached
  }    

  /* Check TH_SHD flag: if not set, the thermal shut down threshold is reached */
  if ((statusRegister & L6474_STATUS_TH_SD) == 0)
  {
    //thermal shut down threshold is reached * 
  }    

  /* Check OCD  flag: if not set, there is an overcurrent detection */
  if ((statusRegister & L6474_STATUS_OCD) == 0)
  {
    //overcurrent detection 
  }      
}
