#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>
#include <Servo.h>

RF24 radio(9, 10);            // CE, CSN
const byte address[6] = "CAR01";

Servo myServo;

const int SERVO_PIN = 6;
bool servoAttached = false;
int currentServoAngle = 90;

const int MOTOR_IN1 = 4;   // -> DRV8833 IN1 (P12 on your board)
const int MOTOR_IN2 = 5;   // -> DRV8833 IN2 (P11 on your board)

void attachServoIfNeeded() {
  if (!servoAttached) {
    myServo.attach(SERVO_PIN);
    servoAttached = true;
  }
}

void detachServoIfNeeded() {
  if (servoAttached) {
    myServo.detach();
    servoAttached = false;
  }
}

void smoothServoMove(int targetAngle) {
  attachServoIfNeeded();
  targetAngle = constrain(targetAngle, 0, 180);

  int stepDir = (targetAngle > currentServoAngle) ? 1 : -1;

  while (currentServoAngle != targetAngle) {
    currentServoAngle += stepDir;
    myServo.write(currentServoAngle);
    delay(12);
  }
}

void handleServo(const String &state, int angle) {
  angle = constrain(angle, 0, 180);

  if (state == "ON") {
    smoothServoMove(angle);
    Serial.print("Servo ON, angle = ");
    Serial.println(angle);
  } else if (state == "OFF") {
    detachServoIfNeeded();
    Serial.print("Servo OFF, angle = ");
    Serial.println(angle);
  } else {
    Serial.println("Unknown SERVO state");
  }
}

void motorForward() {
  digitalWrite(MOTOR_IN1, HIGH);
  digitalWrite(MOTOR_IN2, LOW);
}

void motorBackward() {
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, HIGH);
}

void motorStop() {
  digitalWrite(MOTOR_IN1, LOW);
  digitalWrite(MOTOR_IN2, LOW);
}

void handleDC(const String &action) {
  if (action == "FORWARD") {
    motorForward();
    Serial.println("DC motor FORWARD");
  } else if (action == "BACKWARD") {
    motorBackward();
    Serial.println("DC motor BACKWARD");
  } else if (action == "STOP") {
    motorStop();
    Serial.println("DC motor STOP");
  } else {
    Serial.println("Unknown DC action");
  }
}

void processCommand(String cmd) {
  cmd.trim();

  int firstComma = cmd.indexOf(',');
  int secondComma = cmd.indexOf(',', firstComma + 1);

  if (firstComma < 0 || secondComma < 0) {
    Serial.println("Invalid command format");
    return;
  }

  String type = cmd.substring(0, firstComma);
  String action = cmd.substring(firstComma + 1, secondComma);
  String valueText = cmd.substring(secondComma + 1);
  int value = valueText.toInt();

  if (type == "SERVO") {
    handleServo(action, value);
  } else if (type == "DC") {
    handleDC(action);
  } else {
    Serial.println("Unknown command type");
  }
}

void setup() {
  Serial.begin(115200);

  pinMode(MOTOR_IN1, OUTPUT);
  pinMode(MOTOR_IN2, OUTPUT);
  motorStop();

  if (!radio.begin()) {
    Serial.println("RF24 radio not responding");
    while (1) {}
  }

  radio.setPALevel(RF24_PA_LOW);   // start with LOW for bench testing
  radio.setDataRate(RF24_1MBPS);
  radio.openReadingPipe(0, address);
  radio.startListening();

  Serial.println("Nano RF receiver ready.");
}

void loop() {
  if (radio.available()) {
    char payload[32] = {0};
    radio.read(&payload, sizeof(payload));

    String cmd = String(payload);
    Serial.print("RX: ");
    Serial.println(cmd);

    processCommand(cmd);
  }
}
