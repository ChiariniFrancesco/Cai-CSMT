/*
 * prova1_mvd.ino - Simulatore MVD2555 con protocollo HBM
 *
 * Lo sketch ascolta la seriale come farebbe l'amplificatore HBM/MVD2555
 * vero, e risponde con valori in formato HBM. Quando arriverà l'MVD2555
 * reale, il codice Python NON dovrà cambiare: stessa porta, stessi comandi.
 *
 * Comandi accettati:
 *   \x12 (CTRL+R) -> attiva "remote control state"
 *   AID?\r\n      -> identificazione (risposta: HBM,MVD2555-SIM,0,P15\r\n)
 *   COF1\r\n      -> imposta output ASCII semplice (risposta: 0\r\n)
 *   CPV\r\n       -> clear peak value (risposta: 0\r\n)
 *   TAR\r\n       -> tara (risposta: 0\r\n)
 *   MSV?1,0\r\n   -> avvia streaming continuo del valore
 *   STP\r\n       -> ferma lo streaming
 *   \x01 (CTRL+A) -> chiude remote control
 *
 * Output durante streaming: una riga per misura, formato HBM:
 *   "0.0\r\n"          (valore zero)
 *   "1,234.5\r\n"      (formato anglosassone: virgola = migliaia, punto = decimali)
 *
 * Per testare manualmente dal Serial Monitor:
 *   - Impostare "No line ending" e mandare il singolo carattere CTRL+R
 *     (in alternativa, lo sketch parte in remote anche su MSV?1,0)
 *   - Impostare "Both NL & CR" e mandare "MSV?1,0" per veder partire la rampa
 *   - Mandare "STP" per fermarla
 */

// Parametri della rampa simulata
#define DELAY_MS    100   // 10 misure/secondo = sample rate dell'MVD2555 vero
#define SLOPE       0.5
#define SOLUTION    80
#define RAMP_STOP   64

// Stato interno
int count = 0;
float y = 0.0;
bool streaming = false;        // siamo in MSV?1,0?
bool remoteActive = false;     // remote control attivo (post CTRL+R)?
String cmdBuffer = "";         // accumulo del comando in arrivo


void setup() {
  Serial.begin(9600);  // 8 bit, parity EVEN, 1 stop bit (come MVD2555)
  // Nessun messaggio "Accensione": l'MVD2555 vero non lo manderebbe.
}


void loop() {
  // ---------- 1. Lettura caratteri dalla seriale ----------
  while (Serial.available() > 0) {
    char c = Serial.read();

    // CTRL+R (\x12): attiva remote control
    if (c == 0x12) {
      remoteActive = true;
      cmdBuffer = "";
      continue;
    }
    // CTRL+A (\x01): chiude remote control
    if (c == 0x01) {
      remoteActive = false;
      streaming = false;
      cmdBuffer = "";
      continue;
    }

    // Fine comando: \r o \n. Processiamo il buffer.
    if (c == '\r' || c == '\n') {
      if (cmdBuffer.length() > 0) {
        handleCommand(cmdBuffer);
        cmdBuffer = "";
      }
      continue;
    }

    // Altri caratteri: si accumulano nel buffer
    cmdBuffer += c;
  }

  // ---------- 2. Se siamo in streaming, manda una misura ----------
  if (streaming) {
    if (count <= RAMP_STOP) {
      y = -SLOPE * (float)(count - SOLUTION) * (float)count;
    }
    // dopo RAMP_STOP, y resta congelato (come faceva lo sketch originale)

    sendHbmValue(y);
    count++;
    delay(DELAY_MS);
  }
}


// Gestisce un comando completo arrivato sulla seriale
void handleCommand(String cmd) {
  cmd.trim();
  cmd.toUpperCase();

  if (cmd == "AID?") {
    Serial.print("HBM,MVD2555-SIM,0,P15\r\n");
  }
  else if (cmd.startsWith("COF")) {
    // Accettiamo COF1 (ASCII solo valore) - non implementiamo davvero
    // i formati binari/BCD, ma rispondiamo OK come farebbe il dispositivo.
    Serial.print("0\r\n");
  }
  else if (cmd == "CPV") {
    y = 0;
    count = 0;
    Serial.print("0\r\n");
  }
  else if (cmd == "TAR") {
    // Tara: azzera la baseline. Nel simulatore basta resettare.
    y = 0;
    count = 0;
    Serial.print("0\r\n");
  }
  else if (cmd.startsWith("MSV?")) {
    // MSV?1,0  -> streaming infinito del valore gross
    // MSV?1,1  -> singolo valore (lo trattiamo come uno shot)
    streaming = true;
    count = 0;
    y = 0;
    remoteActive = true;
  }
  else if (cmd == "STP") {
    streaming = false;
  }
  else if (cmd == "DCL") {
    streaming = false;
    remoteActive = false;
  }
  else {
    // Comando sconosciuto
    Serial.print("?\r\n");
  }
}


// Manda un valore nel formato HBM: "1,234.5\r\n"
// Per semplicità nel simulatore usiamo 1 decimale.
void sendHbmValue(float value) {
  long intPart = (long)value;
  int decPart = (int)((value - intPart) * 10.0);
  if (decPart < 0) decPart = -decPart;

  // Costruisci la parte intera con i separatori delle migliaia (virgole)
  String intStr = String(abs(intPart));
  String withCommas = "";
  int len = intStr.length();
  for (int i = 0; i < len; i++) {
    withCommas += intStr.charAt(i);
    int fromRight = len - i - 1;
    if (fromRight > 0 && fromRight % 3 == 0) {
      withCommas += ",";
    }
  }
  if (intPart < 0) withCommas = "-" + withCommas;

  Serial.print(withCommas);
  Serial.print(".");
  Serial.print(decPart);
  Serial.print("\r\n");
}