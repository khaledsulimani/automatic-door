import cv2
import numpy as np
import serial
import time
import os
from datetime import datetime

class SmartDoorSystem:
    def __init__(self, arduino_port='COM3', baud_rate=9600):
        """
        Initialize the Smart Door System
        
        Args:
            arduino_port (str): COM port for Arduino connection
            baud_rate (int): Baud rate for serial communication
        """
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Try to connect to Arduino
        try:
            self.arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
            time.sleep(2)  # Give Arduino time to initialize
            print(f"Connected to Arduino on {arduino_port}")
        except serial.SerialException:
            print(f"Could not connect to Arduino on {arduino_port}. Please check the connection.")
            self.arduino = None
        
        # Face recognition variables
        self.known_faces = []
        self.known_names = []
        self.is_trained = False
        
        # Create directories for storing face data
        if not os.path.exists('known_faces'):
            os.makedirs('known_faces')
        if not os.path.exists('captured_faces'):
            os.makedirs('captured_faces')
    
    def capture_face_samples(self, name, num_samples=30):
        """
        Capture face samples for training
        
        Args:
            name (str): Name of the person
            num_samples (int): Number of face samples to capture
        """
        # Try DirectShow backend first (better for Windows), then try other indices
        cap = None
        
        # Try DirectShow backend with camera 0
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                print(f"Using camera 0 with DirectShow backend")
            else:
                cap.release()
                cap = None
        
        # If DirectShow failed, try regular method with different indices
        if cap is None:
            for camera_index in range(3):
                temp_cap = cv2.VideoCapture(camera_index)
                if temp_cap.isOpened():
                    ret, test_frame = temp_cap.read()
                    if ret and test_frame is not None:
                        cap = temp_cap
                        print(f"Using camera index {camera_index}")
                        break
                    else:
                        temp_cap.release()
                else:
                    temp_cap.release()
        
        if cap is None:
            print("❌ Error: No working camera found!")
            print("Please check:")
            print("- Camera is connected properly")
            print("- No other applications are using the camera")
            print("- Camera drivers are installed")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        count = 0
        face_detected_count = 0
        
        print(f"Capturing face samples for {name}. Press 'q' to quit early.")
        print("📸 Position your face in front of the camera")
        print("💡 Make sure you have good lighting")
        print("🎯 Face detection will start automatically when a face is found")
        
        while count < num_samples:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to read from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Improve contrast for better face detection
            gray = cv2.equalizeHist(gray)
            
            # More sensitive face detection parameters for laptop cameras
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05,      # Smaller scale factor for better detection
                minNeighbors=3,        # Lower threshold for detection
                minSize=(80, 80),      # Smaller minimum face size
                maxSize=(400, 400),    # Maximum face size
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # Display instructions
            cv2.putText(frame, f'Samples: {count}/{num_samples}', (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, 'Press Q to quit', (10, 70), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Debug info
            cv2.putText(frame, f'Faces found: {len(faces)}', (10, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            
            if len(faces) > 0:
                face_detected_count += 1
                # Only capture every 3rd frame when face is detected (to avoid too similar images)
                if face_detected_count % 3 == 0:
                    for (x, y, w, h) in faces:
                        count += 1
                        # Save face sample with some padding
                        padding = 20
                        y_start = max(0, y - padding)
                        y_end = min(gray.shape[0], y + h + padding)
                        x_start = max(0, x - padding)
                        x_end = min(gray.shape[1], x + w + padding)
                        
                        face_sample = gray[y_start:y_end, x_start:x_end]
                        cv2.imwrite(f'known_faces/{name}_{count}.jpg', face_sample)
                        
                        # Draw rectangle around face
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        cv2.putText(frame, f'{name} - Captured!', 
                                   (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        
                        # Flash effect
                        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (255, 255, 255), 10)
                        break
                
                # Draw detection rectangles for all faces
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(frame, 'Face Detected', 
                               (x, y-35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            else:
                cv2.putText(frame, 'No face detected - Move closer to camera', (10, 110), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow('Capturing Face Samples', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or count >= num_samples:
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if count > 0:
            print(f"✅ Successfully captured {count} samples for {name}")
        else:
            print("❌ No face samples were captured. Please try again with better lighting.")
    
    def train_face_recognizer(self):
        """
        Train the face recognizer with captured samples
        """
        faces = []
        labels = []
        
        if not os.path.exists('known_faces'):
            print("No known faces directory found. Please capture face samples first.")
            return False
        
        # Read all face samples
        for filename in os.listdir('known_faces'):
            if filename.endswith('.jpg'):
                name = filename.split('_')[0]
                if name not in self.known_names:
                    self.known_names.append(name)
                
                # Read face image
                face_img = cv2.imread(f'known_faces/{filename}', cv2.IMREAD_GRAYSCALE)
                faces.append(face_img)
                labels.append(self.known_names.index(name))
        
        if len(faces) > 0:
            # Train the recognizer
            self.face_recognizer.train(faces, np.array(labels))
            self.is_trained = True
            print(f"Face recognizer trained with {len(faces)} samples for {len(self.known_names)} people")
            return True
        else:
            print("No face samples found for training")
            return False
    
    def send_servo_command(self, command):
        """
        Send command to Arduino to control servo
        
        Args:
            command (str): 'OPEN' or 'CLOSE'
        """
        if self.arduino:
            try:
                # Clear any pending data
                self.arduino.flushInput()
                self.arduino.flushOutput()
                
                # Send command with proper encoding
                command_with_newline = f"{command}\n"
                self.arduino.write(command_with_newline.encode('utf-8'))
                
                # Wait a moment for Arduino to process
                time.sleep(0.1)
                
                # Try to read response
                if self.arduino.in_waiting > 0:
                    response = self.arduino.readline().decode('utf-8').strip()
                    print(f"Arduino response: {response}")
                
                print(f"✅ Sent command to Arduino: {command}")
                
            except serial.SerialException as e:
                print(f"❌ Failed to send command to Arduino: {e}")
                # Try to reconnect
                try:
                    self.arduino.close()
                    time.sleep(0.5)
                    self.arduino = serial.Serial('COM3', 9600, timeout=1)
                    time.sleep(1)
                    print("🔄 Reconnected to Arduino")
                except:
                    print("🔌 Arduino disconnected")
                    self.arduino = None
        else:
            print(f"❌ Arduino not connected. Would send: {command}")
    
    def recognize_face(self, face_img):
        """
        Recognize a face using the trained model
        
        Args:
            face_img: Grayscale face image
            
        Returns:
            tuple: (name, confidence) or (None, None) if not recognized
        """
        if not self.is_trained:
            return None, None
        
        label, confidence = self.face_recognizer.predict(face_img)
        
        # Lower confidence means better match (0 is perfect match)
        if confidence < 100:  # Threshold for recognition
            name = self.known_names[label]
            return name, confidence
        else:
            return None, None
    
    def run_door_system(self):
        """
        Main loop for the smart door system
        """
        if not self.is_trained:
            print("Face recognizer not trained. Please train first.")
            return
        
        # Try DirectShow backend first (better for Windows), then try other indices
        cap = None
        
        # Try DirectShow backend with camera 0
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                print(f"Using camera 0 with DirectShow backend")
            else:
                cap.release()
                cap = None
        
        # If DirectShow failed, try regular method with different indices
        if cap is None:
            for camera_index in range(3):
                temp_cap = cv2.VideoCapture(camera_index)
                if temp_cap.isOpened():
                    ret, test_frame = temp_cap.read()
                    if ret and test_frame is not None:
                        cap = temp_cap
                        print(f"Using camera index {camera_index}")
                        break
                    else:
                        temp_cap.release()
                else:
                    temp_cap.release()
        
        if cap is None:
            print("❌ Error: No working camera found!")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        door_open = False
        last_recognition_time = 0
        
        print("Smart Door System Running. Press 'q' to quit.")
        print("Authorized users:", ", ".join(self.known_names))
        
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("Failed to read from camera")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Improve contrast for better face detection
            gray = cv2.equalizeHist(gray)
            
            # More sensitive face detection parameters for laptop cameras
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.05,      # Smaller scale factor for better detection
                minNeighbors=3,        # Lower threshold for detection
                minSize=(80, 80),      # Smaller minimum face size
                maxSize=(400, 400),    # Maximum face size
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            current_time = time.time()
            face_recognized = False
            
            for (x, y, w, h) in faces:
                face_roi = gray[y:y+h, x:x+w]
                name, confidence = self.recognize_face(face_roi)
                
                if name:
                    # Authorized face detected
                    face_recognized = True
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, f'{name} - Welcome!', 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(frame, f'Confidence: {confidence:.1f}', 
                               (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    if not door_open:
                        self.send_servo_command('OPEN')
                        door_open = True
                        last_recognition_time = current_time
                        print(f"Door opened for {name} (confidence: {confidence:.1f})")
                
                else:
                    # Unknown face detected
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    cv2.putText(frame, 'Unknown - Access Denied', 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    # Save unknown face for review
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(f'captured_faces/unknown_{timestamp}.jpg', face_roi)
            
            # Auto-close door after 5 seconds if no authorized face detected
            if door_open and (current_time - last_recognition_time > 5) and not face_recognized:
                self.send_servo_command('CLOSE')
                door_open = False
                print("Door closed automatically")
            
            # Display door status
            status_color = (0, 255, 0) if door_open else (0, 0, 255)
            status_text = "DOOR: OPEN" if door_open else "DOOR: CLOSED"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            
            cv2.imshow('Smart Door System', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Clean up
        if door_open:
            self.send_servo_command('CLOSE')
        
        cap.release()
        cv2.destroyAllWindows()
        if self.arduino:
            self.arduino.close()

def main():
    # Initialize the smart door system
    door_system = SmartDoorSystem('COM3')  # Change COM port as needed
    
    print("Smart Door System Setup")
    print("1. Capture face samples")
    print("2. Train face recognizer")
    print("3. Run door system")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            name = input("Enter the person's name: ").strip()
            if name:
                door_system.capture_face_samples(name)
        
        elif choice == '2':
            if door_system.train_face_recognizer():
                print("Training completed successfully!")
            else:
                print("Training failed. Please capture face samples first.")
        
        elif choice == '3':
            door_system.run_door_system()
        
        elif choice == '4':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
