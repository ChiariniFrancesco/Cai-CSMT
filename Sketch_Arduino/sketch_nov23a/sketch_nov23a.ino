#define PIN_RAMP 6
#define PIN_RESET 7
#define SLOPE 0.012
#define SOLUTION 500
#define DELAY 100
#define RAMP_STOP 325

unsigned long t_start_ramp = 0;
unsigned long count = 0; //tempo
float y = 0; //valore rampa
float ymax = 0; //max
bool ramp_active = false; //flag 
bool flag_communication = false;
String command = "";
bool flag_command = false, flag_baud_rate = false, flag_232 = false, flag_cof = false;
int start_communication = 0;

void setup() {
  // put your setup code here, to run once:
  pinMode(PIN_RAMP, INPUT);
  pinMode(PIN_RESET, INPUT);
  Serial.begin(9600);
  Serial.print("Accensione\n Attendo comandi\n");
}

void loop() {
  // put your main code here, to run repeatedly:
  if(digitalRead(PIN_RESET) == HIGH){
    t_start_ramp = millis();
    count = 0;
    y = 0;
    ymax = 0;
    ramp_active = false;
  }

  if(digitalRead(PIN_RAMP) == HIGH){
    ramp_active = true;
  }


  if(ramp_active){
    count = millis() - t_start_ramp;
    if(count <= RAMP_STOP){
      y = -SLOPE*(count - SOLUTION)*count; //max(250, 750), roots 0, 500, stop at (325, 682.5)
    }
     
    if(y > ymax)
      ymax = y;
    
    
  }
  
  if (Serial.available()) {           //seriale funziona?
        if(!flag_communication){     
          start_communication = Serial.read();
          if (start_communication == 18 || start_communication == 2){
            Serial.println("Comunicazione inizializzata");
            flag_communication = true;
          }
          else
          Serial.println("Comunicazione seriale non inizializzata correttamente");
        }
      if(flag_communication){
        command = Serial.readStringUntil(')');
        command.trim();
        command.replace(" ", "");
        command += ')';
        command.trim();
        flag_command = true;  //flag per eseguire il comando
      }
    }


  if (flag_command == true){
    if(command == "BDR6,2,1(x)"){
      flag_baud_rate = true;
      Serial.println("Baud rate settato");
    }
    if(command == "ADR0(x)"){
      flag_232 = true;
      Serial.println("Protocollo seriale settato");
    }
    if(command == "COF0(x)"){
      flag_cof = true;
      Serial.println("Formato ASCII settato");
    }

    if (flag_baud_rate && flag_232 && flag_cof){
      if (command == "MSV?3,1(x)")
        Serial.print(ymax);
      
      if(command == "CLV(x)")
        ymax = 0;
    }
    else{
      Serial.println("Setting non terminato");
    }
    flag_command = false;  //reset flag di comando
    }

  }


