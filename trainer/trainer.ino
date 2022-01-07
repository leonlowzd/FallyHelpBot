/*
    MPU6050 Triple Axis Gyroscope & Accelerometer. Simple Accelerometer Example.
    Read more: http://www.jarzebski.pl/arduino/czujniki-i-sensory/3-osiowy-zyroskop-i-akcelerometr-mpu6050.html
    GIT: https://github.com/jarzebski/Arduino-MPU6050
    Web: http://www.jarzebski.pl
    (c) 2014 by Korneliusz Jarzebski
*/

#include <Wire.h>
#include <MPU6050.h>
#define BEETLE_ID '0'
#include <CRCx.h>

MPU6050 mpu;
const int DELAY = 75;
const float SENSITIVITY = 0.50;
const float GYRO_SENSITIVITY = 1.1;
char hs_msg[] = "HANDSHAKE";
char ack_msg[] = "ACK";

uint8_t data[15];
uint8_t packet[19];
char temp_msg[15];

float data_set[6];

float pitch = 0;
float roll = 0;
float yaw = 0;

float accelX = 0, accelY = 0, accelZ = 0;

float gyroX = 0, gyroY = 0, gyroZ = 0;

float pitch_angle =0;
float roll_angle =0;

float acclAngleX=0;
float acclAngleY=0;
float timeStep = 0.01;

bool handshake = false;
bool handshake_confirmed = false;
bool danceBegin = false;
bool dataBegin = false;
bool stationary = false;


float accErrorX = 0, accErrorY = 0, accErrorZ = 0, gyroErrorX = 0, gyroErrorY = 0, gyroErrorZ = 0;
double tempX = 0, tempY = 0;
float ftempX = 0, ftempY = 0;
int i = 0;
float AccXMean = 0.0, AccYMean = 0.0;

//isMoving global variables
int buffer_size = 5;
float _buffer[5];
int buffer_index = 0;
bool moveToggle = false;
bool dataOverwrite= false;
void setup()
{
  Serial.begin(115200);
  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_4G)) //begin the I2C transmission
  {
    Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
    delay(500);
  }
  calibrate_IMU();
  mpu.calibrateGyro(); // Calibrate gyroscope. The calibration must be at rest.



}

void runIMU(){

  Vector rawAccel = mpu.readRawAccel();
  Vector normAccel = mpu.readNormalizeAccel(); //normalized value for accel
  Vector normGyro = mpu.readNormalizeGyro();      //normalized value for gyro

  pitch_angle = -(atan2(normAccel.XAxis, sqrt(normAccel.YAxis*normAccel.YAxis + normAccel.ZAxis*normAccel.ZAxis))*180.0)/M_PI;
  roll_angle = (atan2(normAccel.YAxis, normAccel.ZAxis)*180.0)/M_PI;

  //16bits data, each into 4 bytes float
  accelX = normAccel.XAxis;
  accelY = normAccel.YAxis;
  accelZ = normAccel.ZAxis;

  //16 bits data, each into 4 bytes float
  gyroX = gyroX + normGyro.XAxis;
  gyroY = gyroY + normGyro.YAxis;
  gyroZ = gyroZ + normGyro.ZAxis;

  // Correct the outputs with the calculated error values
  gyroX = gyroX - gyroErrorX;
  gyroY = gyroY - gyroErrorY;
  gyroZ = gyroZ - gyroErrorZ;

  gyroX = gyroX * timeStep;
  gyroY = gyroY * timeStep;
  gyroZ = gyroZ * timeStep;



  // Correct the outputs with the calculated error values
  accelX = accelX - accErrorX;
  accelY = accelY - accErrorY;
  accelZ = accelZ - accErrorZ;

  // Complementary filter - accel (low pass filter) and gyro (high pass filter)
  roll = (0.96 * gyroX) + (0.04 * accelX);
  pitch = (0.96 * gyroY) + (0.04 * accelY);
  yaw = (0.96 * gyroZ) + (0.04 * accelZ);

  //data already is in 2dp, x100 to easier define them in characters

    data_set[0] = accelX;
    data_set[1] = accelY;
    data_set[2] = accelZ;
    data_set[3] = roll; //roll
    data_set[4] = pitch; // pitch
    data_set[5] = yaw; //yaw
    
  if(dataOverwrite) {
    // Output acceleration x,y,z
    Serial.print(0.0);
    Serial.print(",");
    Serial.print(0.0);
    Serial.print(",");
    Serial.print(0.0);

    // Output row, pitch, yaw
    Serial.print(",");
    Serial.print(data_set[3]);
    Serial.print(",");
    Serial.print(data_set[4]);
    Serial.print(",");
    Serial.println(data_set[5]);
  }
  else {
  // Output acceleration x,y,z
    Serial.print(accelX);
    Serial.print(",");
    Serial.print(accelY);
    Serial.print(",");
    Serial.print(accelZ);

    // Output row, pitch, yaw
    Serial.print(",");
    Serial.print(roll);
    Serial.print(",");
    Serial.print(pitch);
    Serial.print(",");
    Serial.println(yaw);
  }

}

// Calculate accelerometer and gyro data error to prevent values drifting
void calibrate_IMU() {

  int c = 0;

  // Read accelerometer values 200 times and get the average
  while (c < 50) {
    // Take accelerometer reading
    Vector rawAccel = mpu.readRawAccel();
    Vector normAccel = mpu.readNormalizeAccel(); //normalized value for accel
    Vector normGyro = mpu.readNormalizeGyro();      //normalized value for gyro

    accelX = normAccel.XAxis;
    accelY = normAccel.YAxis;
    accelZ = normAccel.ZAxis;


    accErrorX = accErrorX + accelX;
    accErrorY = accErrorY + accelY;
    accErrorZ = accErrorZ + accelZ;
    c++;
  }
  //Divide the sum by 300 to get the error value
  accErrorX = accErrorX / 50;
  accErrorY = accErrorY / 50;
  accErrorZ = accErrorZ / 50;
  c = 0;

  // Read gyro values 300 times and get the average
  while (c < 50) {
    // Take gyro reading
    Vector rawAccel = mpu.readRawAccel();
    Vector normAccel = mpu.readNormalizeAccel(); //normalized value for accel
    Vector normGyro = mpu.readNormalizeGyro();      //normalized value for gyro

    gyroX = gyroX + normGyro.XAxis * timeStep;
    gyroY = gyroY + normGyro.YAxis * timeStep;
    gyroZ = gyroZ + normGyro.ZAxis * timeStep;

    // Sum all readings
    gyroErrorX = gyroErrorX + gyroX;
    gyroErrorY = gyroErrorY + gyroY;
    gyroErrorZ = gyroErrorZ + gyroZ;
    c++;
  }

  //Divide the sum by 300 to get the error value
  gyroErrorX = gyroErrorX / 50;
  gyroErrorY = gyroErrorY / 50;
  gyroErrorZ = gyroErrorZ / 50;
}


//prepare data to fill them to 14bytes
void prepareData(char packet[]){

 // int packet_length = strlen(packet);
  int j = strlen(packet) -1;

  //fill the array up
  for(int i = 13; i>=0; i--){
     if(j>=0){
      data[i] = packet[j--]; //char into uint8
     }else{
      data[i] = '*';
     }
  }


}

void preparePacket(char packetID){

  uint8_t result8 = crcx::crc8(data, 14); //1 byte result
  String temp = String(result8, HEX); // change to string in hex
  char crcValue[3];
  temp.toCharArray(crcValue, 3);//store them as char array

  packet[0] = BEETLE_ID;
  packet[1] = packetID;
  int j = 0;
  for(int i =2; i<16; i++){
   packet[i]= data[j++];
  }

  if (strlen(crcValue) == 1) { //pad it into size of 2 byte
    packet[16] = '0';
    packet[17] = crcValue[0];
  } else {
    packet[16] = crcValue[0];
    packet[17] = crcValue[1];
  }

}

//prepare 3 packets to be send
void sendPacket(){
  String stringData;
  String accelData; //starting from x -> y -> z
  String gyroData;
  int i = 1;
  int accel_set_no = 0;
  int gyro_set_no = 3;
  int packetID = 49; // 1 in ASCII


  //loop 3x for each axle
  while(i < 4){
    accelData = String(data_set[accel_set_no++]);
    gyroData = String(data_set[gyro_set_no++]);
    stringData = accelData + "|" + gyroData; //concat the string together
    stringData.toCharArray(temp_msg, 15);  //convert them to char array of 17 bytes
    prepareData(temp_msg);             //padding to fill up 16 bytes
    preparePacket(char (packetID));    //pack the packets
    Serial.println((char*)packet);
    Serial.flush();
    Serial.print("Packet Size = ");
    Serial.println(sizeof(packet));

    memset(temp_msg, 0, 15);
    memset(data, 0, 15);
    memset(data_set, 0, sizeof(float));
    i+=1;
    packetID+=1;
  }
}

float standard_deviation(float values[5]){

  float mean =0;
  float temp =0;
  for (int i = 0; i < buffer_size; ++i) {
    mean = mean +values[i];
  }
  mean = mean/buffer_size;

  for (int i = 0; i < buffer_size; ++i) {
    temp = temp + ((values[i] - mean)*(values[i] - mean));
  }

  return sqrt(temp/buffer_size);
}

bool isMoving(float value) {
  buffer_index = (buffer_index + 1) % buffer_size;
  _buffer[buffer_index] = value;
//  Serial.println(standard_deviation(_buffer));
  if(standard_deviation(_buffer)> SENSITIVITY ) return true; //exceeds threshold
  else return false;
}


void loop()
{
  if(!isMoving(data_set[0]) && abs(data_set[3])<GYRO_SENSITIVITY && abs(data_set[4])<GYRO_SENSITIVITY && abs(data_set[5])<GYRO_SENSITIVITY){
    dataOverwrite = true;
    if(!moveToggle){
//      Serial.println("Calibrated");
//      calibrate_IMU();
      moveToggle = true;
    }
  }
  else {
    dataOverwrite = false;
    moveToggle = false;
  }
runIMU();


if(Serial.available()){ //read serial port

byte cmd = Serial.read();

  switch(cmd){

    case 'A': //receive ack from laptop
//    prepareData(ack_msg); //send a back ack
//    preparePacket('3'); //ack ID 0->3 , 1 ->4, 2->5
//    Serial.print((char*)packet); //send packet
//    Serial.flush();
//    memset(data, 0, 15); //clear data

    if (handshake) {
      handshake = false; //reset
      handshake_confirmed = true;
        }
    if (handshake_confirmed) {
      danceBegin = true;
        }

    break;

    case 'H': //receive a handshake request
    prepareData(hs_msg);
    preparePacket('3'); ////handshake ID 0->3 , 1 ->4, 2->5
    Serial.print((char*)packet); //send packet
    Serial.flush();
    memset(data, 0, 15); //clear data
    danceBegin = false;
    handshake = true;
    handshake_confirmed = false;
  }


  if(danceBegin && handshake_confirmed){ //send dance data
    runIMU();
    sendPacket();
  }

}
  delay(DELAY);
}

void detectStartDance(){

if( abs(data_set[0])>5 || abs(data_set[1])>5 || abs(data_set[2])>5 || abs(data[3])>1 || abs(data[4])>1 || abs(data[5])>1 ){
    danceBegin = true;
    stationary = false;
  }
else{
    stationary = true;
    danceBegin = false;
  }
}
