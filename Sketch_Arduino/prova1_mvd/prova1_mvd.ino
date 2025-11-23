#define PIN_RAMP 6
#define PIN_RESET 7
#define SLOPE 0.5
#define SOLUTION 80
#define DELAY 100
#define RAMP_STOP 64


int count = 0; //contatore ciclo
int y = 0; //valore rampa
int ymax = 0; //max
bool ramp_active = false; //flag 

void setup() {
  // put your setup code here, to run once:
  pinMode(PIN_RAMP, INPUT);
  pinMode(PIN_RESET, INPUT);
  Serial.begin(9600);
  Serial.print("Accensione\n");
}

void loop() {
  // put your main code here, to run repeatedly:
  if(digitalRead(PIN_RESET) == HIGH){
    count = 0;
    y = 0;
    ymax = 0;
    ramp_active = false;
  }

  if(digitalRead(PIN_RAMP) == HIGH){
    ramp_active = true;
  }


  if(ramp_active){
    if(count <= RAMP_STOP){
      y = -SLOPE*(count - SOLUTION)*count; //grafico: https://www.desmos.com/calculator/7pryfwphdk
    }
     
    if(y > ymax)
      ymax = y;
    delay(DELAY); //ritardo rampa
    count++;
  }
  Serial.print("y = ");
  Serial.print(y);
  Serial.print("\nymax = ");
  Serial.print(ymax);
  Serial.print("\n");

}
