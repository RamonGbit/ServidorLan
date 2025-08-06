# Simulador de Red LAN - CLI estilo Router

Un simulador de red LAN escrito en Python con una interfaz de línea de comandos inspirada en la sintaxis de routers Cisco. Permite crear dispositivos, configurar interfaces, establecer conexiones, enviar paquetes y visualizar el estado de la red y estadísticas.

## Características

- Crear dispositivos de tipo Router, Switch, Host y Firewall.
- Configurar interfaces: asignar IP, cambiar estado (up/down).
- Conectar y desconectar interfaces entre dispositivos.
- Envío de paquetes con TTL y trazado de ruta.
- Simulación en ticks: cada tick representa un salto de paquete.
- Visualización de colas pendientes (`show queue`), historial de paquetes (`show history`), conexiones (`show connections`) e interfaces (`show interfaces`).
- Métricas: paquetes enviados, entregados y descartados por TTL.
- Guardado y carga de configuración en formato JSON.

## Requisitos

- Python 3.10 o superior

## Instalación y ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/RamonGbit/ServidorLan.git
   cd "ServidorLan"
   ```

2. Ejecuta el simulador:
   ```bash
   python main.py
   ```

## Uso de la CLI

La línea de comandos principal soporta los siguientes comandos:

| Comando                           | Descripción                                      |
|-----------------------------------|--------------------------------------------------|
| hostname <name>                   | Crea o cambia al dispositivo <name>              |
| interface <iface>                 | Entra en modo configuración de interfaz          |
| ip address <ip>                   | Asigna IP a la interfaz activa                  |
| no shutdown / shutdown            | Habilita o deshabilita la interfaz               |
| connect <dev1> <if1> <dev2> <if2>  | Conecta dos interfaces bidireccionalmente       |
| disconnect <dev1> <if1> <dev2> <if2>| Desconecta dos interfaces                       |
| send <src_ip> <dst_ip> <msg> <ttl> | Envía un paquete desde <src_ip> a <dst_ip>      |
| tick / process                    | Avanza un tick de simulación (un salto de paquete)|
| show queue <device>               | Muestra la cola de paquetes pendiente            |
| show history <device>             | Muestra historial de paquetes recibidos          |
| show interfaces <device>          | Muestra estado e IP de interfaces                |
| show connections <device>         | Muestra conexiones de un dispositivo             |
| show statistics                   | Muestra métricas de envío/entrega/descartes      |
| save running-config [<file>]      | Guarda configuración en JSON (default: running-config.json)|
| load config [<file>]              | Carga configuración desde JSON (default: running-config.json)|
| quit / exit                       | Sale de la CLI                                   |

## Formato de Configuración (JSON)

El archivo de configuración JSON contiene dos secciones principales:

```json
{
  "devices": [
    {
      "name": "Router1",
      "device_type": "router",
      "online": true,
      "interfaces": [
        {"name": "g0/0", "ip_address": "192.168.1.1", "status": "up"}
      ]
    }
  ],
  "connections": [
    ["Router1","g0/0","Router2","g0/1"]
  ]
}
```

- `devices`: arreglo de dispositivos con sus interfaces.
- `connections`: lista de arreglos de cuatro elementos `[dev1, iface1, dev2, iface2]`.
