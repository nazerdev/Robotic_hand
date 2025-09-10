//Codigo de prueba del sensor 
#define FLEX_PIN 8  // IO8 (P4)
const int numReadings = 10;
int readings[numReadings];    // Almacén de lecturas
int indice = 0;
int total = 0;
int average = 0;
// Umbrales ajustables para detección
const int dobladoThreshold = 4095;  // se cambia dependiendo del sensor
const int rectoThreshold   = 0;

void setup() {
  Serial.begin(115200);
  analogReadResolution(12); // Rango de 0 a 4095
  for (int i = 0; i < numReadings; i++) {
    readings[i] = 0;
  }
}

void loop() {
  total -= readings[indice];
  readings[indice] = analogRead(FLEX_PIN);
  total += readings[indice];
  indice = (indice + 1) % numReadings;
  average = total / numReadings;
  // Mostrar valor suavizado
  Serial.print("Valor flex (promediado): ");
  Serial.print(average);

  // Lógica de estado
  if (average > dobladoThreshold) {
    Serial.println("  --> Sensor DOBLADO");
  } else if (average < rectoThreshold) {
    Serial.println("  --> Sensor RECTO");
  } else {
    Serial.println("  --> Estado intermedio");
  }
  delay(500);
}
