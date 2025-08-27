#include <Servo.h>

// Create servo object
Servo doorServo;

// Pin definitions
const int SERVO_PIN = 9;        // Servo motor pin

// Servo positions
const int DOOR_CLOSED_ANGLE = 0;    // Door closed position
const int DOOR_OPEN_ANGLE = 90;     // Door open position

// Variables
bool doorOpen = false;
String command = "";

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Small delay for stability
  delay(500);
  
  // Attach servo to pin
  doorServo.attach(SERVO_PIN);
  
  // Initialize door to closed position
  doorServo.write(DOOR_CLOSED_ANGLE);
  delay(500);  // Wait for servo to move
  
  Serial.println("Smart Door System - Arduino Ready");
  Serial.println("Waiting for commands...");
  Serial.println("Servo initialized at closed position");
}

void loop() {
  // Check for incoming serial commands
  if (Serial.available() > 0) {
    command = Serial.readStringUntil('\n');
    command.trim();  // Remove whitespace
    
    // Echo received command for debugging
    Serial.println("Received: " + command);
    
    if (command == "OPEN") {
      openDoor();
    }
    else if (command == "CLOSE") {
      closeDoor();
    }
    else if (command.length() > 0) {
      Serial.println("Unknown command: " + command);
    }
    
    // Flush any remaining serial data
    while(Serial.available() > 0) {
      Serial.read();
    }
  }
  
  delay(50);  // Slightly longer delay for stability
}

void openDoor() {
  if (!doorOpen) {
    Serial.println("Opening door...");
    
    // Move servo to open position smoothly
    doorServo.write(DOOR_OPEN_ANGLE);
    delay(500);  // Wait for movement to complete
    
    doorOpen = true;
    Serial.println("Door opened successfully");
  }
  else {
    Serial.println("Door is already open");
  }
}

void closeDoor() {
  if (doorOpen) {
    Serial.println("Closing door...");
    
    // Move servo to closed position smoothly
    doorServo.write(DOOR_CLOSED_ANGLE);
    delay(500);  // Wait for movement to complete
    
    doorOpen = false;
    Serial.println("Door closed successfully");
  }
  else {
    Serial.println("Door is already closed");
  }
}

// Function to manually test servo movement
void testServo() {
  Serial.println("Testing servo movement...");
  
  // Open
  doorServo.write(DOOR_OPEN_ANGLE);
  delay(1000);
  
  // Close
  doorServo.write(DOOR_CLOSED_ANGLE);
  delay(1000);
  
  Serial.println("Servo test completed");
}
