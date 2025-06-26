# PyNTP Time

**PyNTP Time** é uma biblioteca Python leve e robusta para obter o tempo preciso de servidores NTP (Network Time Protocol). Ela oferece uma interface similar à `time.time()`, retornando timestamps UNIX (float), enquanto gerencia internamente a sincronização, compensação de atraso e atualizações.

Este pacote é um fork e uma refatoração do [ntp-time](https://pypi.org/project/ntp-time/), com o objetivo de modernizar a estrutura do código para uma abordagem orientada a objetos e oferecer maior flexibilidade na configuração.

## Funcionalidades Principais

- **Orientado a Objetos:** Configure e utilize o cliente NTP através de uma instância da classe `NTPTime`.
- **Servidor NTP Configurável:** Especifique o servidor NTP desejado ao instanciar o cliente.
- **Modos de Operação Flexíveis:**
  - **Threaded (Padrão):** Sincronização automática em segundo plano a cada X segundos (configurável), garantindo que chamadas a `now()` sejam rápidas e não realizem acesso à rede no momento da chamada.
  - **Síncrono:** Realiza a sincronização com o servidor NTP a cada chamada do método `now()`. Ideal para casos onde multithreading não é desejado ou para scripts de curta duração que necessitam do tempo mais atualizado possível no momento da consulta.
- **Compensação de Atraso:** Atrasos de comunicação com a Internet são compensados (nota: não há garantia de precisão perfeita).
- **Suavização de Tempo:** Para evitar problemas com o "tempo andando para trás", as correções são aplicadas gradualmente ao longo de um período configurável (padrão: 10 segundos).
- **Backoff Exponencial:** Em caso de falha na conexão, novas tentativas ocorrem com um intervalo crescente.

## Instalação

```bash
pip install pyntp-time
```

_(Nota: Quando o pacote estiver disponível no PyPI. Por enquanto, instale localmente ou via Git.)_

## Como Usar

### Modo Threaded (Padrão)

Neste modo, a sincronização ocorre em uma thread separada em intervalos regulares. O método `now()` retorna o tempo ajustado com base no último offset calculado, tornando-o muito rápido.

```python
import time
from pyntp import NTPTime

# Instancia o cliente NTP (usará pool.ntp.org por padrão e modo threaded)
ntp_client = NTPTime()

# Aguarde alguns segundos para a primeira sincronização em background (especialmente na primeira execução)
# Em aplicações de longa duração, isso não é um problema.
# Para scripts curtos, considere o modo síncrono ou uma espera inicial.
print("Aguardando a primeira sincronização em background...")
time.sleep(5) # Exemplo de espera, pode variar. Idealmente, a biblioteca deve lidar com isso internamente ou fornecer um status.

print("Tempo NTP (Threaded):")
for _ in range(5):
    t = ntp_client.now()
    print(f"Timestamp: {t}, Humano: {time.ctime(t)}")
    time.sleep(1)

# Você pode configurar o servidor e os intervalos:
# ntp_client_custom = NTPTime(ntp_server_url="time.google.com", adjust_interval=300, merge_time=5)
```

### Modo Síncrono (Não-Threaded)

Neste modo, cada chamada a `now()` bloqueará a execução para contatar o servidor NTP e obter o offset mais recente. Isso pode introduzir latência, mas garante que o tempo retornado é o mais atualizado possível no momento da chamada.

```python
import time
from pyntp import NTPTime

# Instancia o cliente NTP em modo síncrono
ntp_client_sync = NTPTime(threaded=False, ntp_server_url="time.cloudflare.com")

print("\nTempo NTP (Síncrono):")
# A primeira chamada pode demorar um pouco mais devido à sincronização inicial no construtor.
# As subsequentes também farão I/O de rede.
for i in range(3):
    print(f"Chamada {i+1}...")
    t_sync = ntp_client_sync.now()
    print(f"Timestamp: {t_sync}, Humano: {time.ctime(t_sync)}")
    time.sleep(1) # Pequena pausa para observar
```

## Configuração da Instância `NTPTime`

O construtor da classe `NTPTime` aceita os seguintes parâmetros:

- `ntp_server_url (str)`: URL do servidor NTP a ser utilizado. (Padrão: `"pool.ntp.org"`)
- `adjust_interval (int)`: Intervalo em segundos para a sincronização automática no modo threaded. (Padrão: `60` segundos)
- `merge_time (int)`: Tempo em segundos durante o qual a correção do offset é gradualmente aplicada. (Padrão: `10` segundos)
- `threaded (bool)`: Se `True` (padrão), opera em modo threaded. Se `False`, opera em modo síncrono.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests.

## Licença

Este projeto é licenciado sob a Licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Agradecimentos

- Este projeto é um fork e uma refatoração do excelente trabalho feito no pacote [ntp-time](https://pypi.org/project/ntp-time/).
