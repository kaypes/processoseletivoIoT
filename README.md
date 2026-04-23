### Console de Comunicação Assistiva por Código Morse

---

## 1. Descrição e Objetivo do Sistema

Um dispositivo assistivo que permite a pessoas com mobilidade reduzida, como portadores de ELA, paralisia cerebral ou lesões medulares severas comunicarem-se por escrito utilizando apenas um botão.

O sistema converte pressionamentos físicos em texto por meio do código morse: um pressionamento curto (< 300 ms) gera um ponto (`.`), um longo (≥ 300 ms) gera um traço (`-`). O silêncio de 800 ms entre pressionamentos é interpretado como fim de caractere, que é então decodificado, exibido no display OLED e confirmado por feedback visual e sonoro.

Um segundo botão (CTRL) inicia ou encerra a sessão de digitação.

**Por que este problema é relevante?**  
Dispositivos comerciais de comunicação assistiva custam entre R$ 5.000 e R$ 30.000 no mercado brasileiro. Esse demonstra que a mesma funcionalidade central pode ser implementada com hardware de baixíssimo custo, arquitetura limpa e firmware profissional.

---

## 2. Hardware e Componentes

Toda a simulação é executada no Wokwi com os seguintes componentes:

| Componente | ID no Diagrama | Conexão GPIO | Função |
|---|---|---|---|
| ESP32 DevKit C v4 | `esp` | — | Microcontrolador principal |
| OLED SSD1306 128×64 | `oled` | SDA: 21 / SCL: 22 | Interface de texto principal |
| Pushbutton (vermelho) | `btn_morse` | GPIO 14 | Entrada Morse — ponto ou traço |
| Pushbutton (azul) | `btn_ctrl` | GPIO 15 | Iniciar / encerrar sessão |
| NeoPixel × 8 | `neo1`–`neo8` | GPIO 27 | Feedback visual da sequência |
| Buzzer passivo | `buzzer` | GPIO 26 | Feedback sonoro (PWM 440 Hz) |

**Convenção de cores dos fios no `diagram.json`:**

| Cor | Significado |
|---|---|
| Vermelho | VCC / 3.3V |
| Preto | GND |
| Verde | I2C SDA e Botão MORSE |
| Amarelo | I2C SCL |
| Laranja | NeoPixel data chain |
| Azul | Botão CTRL |
| Branco | Buzzer PWM |

---

## 3. Arquitetura de Software

### 3.1 Máquina de Estados Finita (FSM)

O núcleo do sistema é uma FSM formal com 5 estados implementada em `fsm.py`:

```
                   CTRL
  ┌──────────────────────────────────────────────┐
  │                                              ▼
IDLE ──(CTRL)──► LISTENING ──(PRESS)──► PRESSING
                  ▲    │                    │
                  │    │ (CHAR_TIMEOUT)     │ (RELEASE)
                  │    ▼                    ▼
                  │  DECODING ◄─────── [mede duração]
                  │    │
                  │    ▼
                  └── FEEDBACK
```

| Estado | Descrição |
|---|---|
| `IDLE` | Sistema aguarda CTRL para iniciar sessão |
| `LISTENING` | Aguarda pressionamento; watchdog de 800 ms ativo |
| `PRESSING` | Botão pressionado; mede duração via `ticks_ms()` |
| `DECODING` | Classifica sequência; decodifica caractere Morse |
| `FEEDBACK` | Animação de confirmação; absorve inputs acidentais |

### 3.2 Fluxo de Dados

```
Botão físico
    │
    ▼
ButtonMatrix._poll_morse()
    │
    │
    ▼
async_queue.Queue.put_nowait()
    │
    ▼
FSM.run() → FSM._dispatch()
    │
    ├── FeedbackController
    ├── DisplayDriver.render()
    └── _watchdog_coro()
```

### 3.3 Bibliotecas e módulos utilizados
| Módulo | Origem | Onde é usado | Finalidade |
|---|---|---|---|
| `uasyncio` | MicroPython stdlib | `main.py`, `fsm.py`, `async_queue.py`, `input_handler.py`, `hal.py` | Event loop, tasks e primitivas assíncronas |
| `machine.Pin` | MicroPython stdlib | `input_handler.py`, `hal.py`, `display_driver.py` | Controle de GPIOs |
| `machine.PWM` | MicroPython stdlib | `hal.py` | Geração de sinal PWM para o buzzer |
| `machine.SoftI2C` | MicroPython stdlib | `display_driver.py` | Comunicação I2C com o display OLED |
| `neopixel` | MicroPython stdlib | `hal.py` | Controle dos LEDs WS2812 |
| `micropython.const` | MicroPython stdlib | `config.py`, `fsm.py`, `hal.py`, `display_driver.py`, `async_queue.py` | Otimização de constantes em tempo de compilação |
| `time` | MicroPython stdlib | `input_handler.py`, `fsm.py` | Medição de duração de pressionamento via `ticks_ms()` |
| `ssd1306` | Bundled no repositório (`src/ssd1306.py`) | `display_driver.py` | Driver oficial do display OLED SSD1306 |
| `framebuf` | MicroPython stdlib | `ssd1306.py` (interno) | Buffer de framebuffer usado pelo driver OLED |

### 3.4 Decisões de Arquitetura

**Por que `async_queue.py` customizada em vez de `uasyncio.Queue`?**  
A classe `uasyncio.Queue` não existe na versão do MicroPython utilizado. A implementação própria baseada em `uasyncio.Event` supre a ausência com comportamento equivalente.  

**Por que polling em vez de IRQ nos botões?**  
IRQ handlers no MicroPython do Wokwi têm limitações de contexto: não podem fazer I/O assíncrono nem interagir com `uasyncio` diretamente. O polling assíncrono com confirmação dupla (lê → aguarda `DEBOUNCE_MS` → confirma) oferece debounce mais robusto no ambiente simulado sem as restrições do contexto de interrupção.   

**Por que `ssd1306.py` no repositório?**  
O boot retornou `ImportError: no module named 'ssd1306'`. O módulo não está presente no binário MicroPython. O driver foi incluído diretamente como solução.

**Por que dividir o firmware em múltiplos arquivos?**   
Cada responsabilidade separada em seu próprio módulo torna o código mais fácil de navegar e de depurar.

---

## 4. Como Executar

### 4.1 Simulação no Wokwi

1. Faça fork ou clone do repositório
2. Acesse [wokwi.com](https://wokwi.com) e importe o projeto
3. Clique em **Play**. O terminal exibirá `Teste` confirmando boot bem-sucedido
4. Pressione **CTRL** (botão azul) para iniciar uma sessão
5. Use **MORSE** (botão vermelho) para digitar: curto = ponto, longo = traço
6. Aguarde 800 ms após o último símbolo para decodificar o caractere
7. Pressione **CTRL** novamente para encerrar e limpar a sessão

**Tabela de referência rápida:**

| Letra | Morse | Letra | Morse | Número | Morse
|---|---|---|---|---|---|
| A | `.-` | N | `-.` | 1 | `.----`
| B | `-...` | O | `---` | 2 | `..---`
| C | `-.-.` | P | `.--.` | 3 | `...--`
| D | `-..` | Q | `--.-` | 4 | `....-`
| E | `.` | R | `.-.` | 5 | `.....`
| F | `..-.` | S | `...` | 6 | `-....`
| G | `--.` | T | `-` | 7 | `--...`
| H | `....` | U | `..-` | 8 | `---..`
| I | `..` | V | `...-` | 9 | `----.`
| J | `.---` | W | `.--` | 0 | `-----`
| K | `-.-` | X | `-..-`
| L | `.-..` | Y | `-.--`
| M | `--` | Z | `--..`

- **Gesto de espaço:** quatro linhas consecutivas (`----`) dão espaço entre duas letras.   
- **Gesto de backspace:** seis ou mais pontos consecutivos (`......`) apagam o último caractere.

---

## 5. Resultados e Funcionamento

Durante a simulação, o display OLED atualiza em tempo real conforme o usuário interage:

- **Linha 1:** estado atual da FSM (`IDLE`, `LISTEN`, `PRESS`, `DECODE`, `OK`)
- **Linha 2:** sequência Morse em construção
- **Linha 3-4:** mensagem acumulada na sessão

Os NeoPixels respondem visualmente a cada símbolo:  
- **Azul** para ponto, **laranja** para traço, acumulando da esquerda para a direita  
- **Verde** em todos os 8 LEDs simultaneamente ao decodificar com sucesso  
- **Apagados** ao retornar para LISTENING, prontos para o próximo caractere  

O buzzer emite tom de 440 Hz enquanto o botão está pressionado, fornecendo feedback auditivo da duração, o que é essencial para usuários que dependem do som para calibrar ponto vs. traço.

---

## 6. Limitações e Trabalhos Futuros

**Limitações atuais:**

| Limitação | Causa | Impacto |
|---|---|---|
| Sem persistência de sessão | Ausência de NVS no ambiente simulado | Mensagem perdida ao resetar |
| Velocidade de digitação limitada | `CHAR_TIMEOUT_MS = 800ms` fixo | Usuários experientes podem querer menos tempo |

**Possíveis extensões:**

- **NVS (Non-Volatile Storage)** do ESP32 para persistir a última mensagem entre resets
- **Velocidade adaptativa** — reduzir `CHAR_TIMEOUT_MS` progressivamente conforme o usuário ganha prática
- **Modo de predição** — sugerir palavras baseado no prefixo digitado, reduzindo o esforço
- **Saída Bluetooth HID** — transmitir o texto diretamente como teclado para celular ou computador, eliminando a necessidade do display

---
