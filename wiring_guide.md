# Arduino Wiring Guide for Smart Door System

## Components List
- 1x Arduino Uno/Nano
- 1x Servo Motor (SG90 or similar)
- 1x Green LED (5mm)
- 1x Red LED (5mm)  
- 1x Active Buzzer (5V)
- 2x 220Ω Resistors (for LEDs)
- 1x Breadboard
- Jumper wires (Male-to-Male and Male-to-Female)

## Pin Connections

### Servo Motor
```
Servo Pin    | Arduino Pin
-------------|-------------
Red (VCC)    | 5V
Black (GND)  | GND
Yellow/White | Pin 9 (PWM)
```

### LEDs
```
Component    | Arduino Pin | Notes
-------------|-------------|------------------
Green LED +  | Pin 7       | Through 220Ω resistor
Green LED -  | GND         |
Red LED +    | Pin 8       | Through 220Ω resistor  
Red LED -    | GND         |
```

### Buzzer
```
Buzzer Pin   | Arduino Pin
-------------|-------------
Positive (+) | Pin 6
Negative (-) | GND
```

## Breadboard Layout

```
    5V  GND  Pin6 Pin7 Pin8 Pin9
     |   |    |    |    |    |
     |   |    |    |    |    |
     |   +----+----+----+----+---- GND Rail
     |        |    |    |    |
     |        |    |    |    +---- Servo Signal (Yellow)
     |        |    |    +--------- Red LED (through 220Ω)
     |        |    +-------------- Green LED (through 220Ω)  
     |        +------------------- Buzzer (+)
     |
     +---------------------------- Servo VCC (Red)

Servo GND (Black) connects to GND rail
LED negative terminals connect to GND rail
Buzzer negative terminal connects to GND rail
```

## Step-by-Step Wiring

### 1. Power Rails
- Connect Arduino 5V to breadboard positive rail
- Connect Arduino GND to breadboard negative rail

### 2. Servo Motor
- Red wire → Arduino 5V
- Black wire → Arduino GND  
- Yellow/White wire → Arduino Pin 9

### 3. Green LED (Door Open Indicator)
- Long leg (Anode) → 220Ω resistor → Arduino Pin 7
- Short leg (Cathode) → Arduino GND

### 4. Red LED (Door Closed Indicator)  
- Long leg (Anode) → 220Ω resistor → Arduino Pin 8
- Short leg (Cathode) → Arduino GND

### 5. Buzzer
- Positive (+) → Arduino Pin 6
- Negative (-) → Arduino GND

## Visual Diagram

```
    Arduino Uno
    +---------+
    |      5V |-----> Red wire (Servo)
    |     GND |-----> Black wire (Servo), LED cathodes, Buzzer (-)
    |         |
    |   Pin 9 |-----> Yellow wire (Servo signal)
    |   Pin 8 |-----> Red LED (through resistor)
    |   Pin 7 |-----> Green LED (through resistor)  
    |   Pin 6 |-----> Buzzer (+)
    |         |
    +---------+
```

## Important Notes

1. **Servo Power**: Make sure servo gets 5V power. Some servos may require external power supply for high-torque applications.

2. **LED Resistors**: Always use 220Ω resistors with LEDs to prevent damage.

3. **Buzzer Type**: Use an active buzzer (has internal oscillator). Passive buzzers require PWM signals.

4. **Wire Management**: Keep wires organized and secure all connections.

5. **Testing**: Test each component individually before connecting everything.

## Common Issues

- **Servo jittery**: Check power supply, ensure good connections
- **LEDs not lighting**: Check polarity and resistor values  
- **Buzzer not working**: Verify it's an active buzzer and polarity is correct
- **Communication issues**: Ensure correct COM port and baud rate (9600)

## Safety Tips

- Double-check all connections before powering on
- Never connect LEDs directly without resistors
- Ensure servo is properly secured if used for actual door mechanism
- Use appropriate power supply for your servo motor
