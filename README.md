# Sistema de Gestão de Acesso - TCC

Este projeto é uma API desenvolvida para o controle de salas de aula e gestão de hardware (RFID e Servomotor) em ambiente escolar. O sistema integra front-end, back-end e hardware para automatizar o agendamento de salas e o controle de entrada.

## 🛠️ Tecnologias Utilizadas
- *Linguagem:* Python
- *Framework:* FastAPI
- *Servidor:* Uvicorn
- *Comunicação:* API REST (JSON)
- *Hardware Integrado:* Arduino/ESP32 com Leitor RFID e Servomotor

## 🚀 Como Executar o Projeto

1. *Pré-requisitos:*
   Certifique-se de ter o Python instalado na sua máquina.

2. *Instalação das dependências:*
   Abra o terminal na pasta do projeto e instale o FastAPI e o Uvicorn:
   ```bash
   pip install fastapi uvicorn




   INICIALIZAÇÃO
   // Se a máquina nao ter o python instalado, python.org/downloads
   //Se tiver mas o windows nao reconhecer, 
  //py -m pip install -r requirements.txt
  //py -m uvicorn main:app --reload
  Se estiver tudo certo python -m pip install -r requirements.txt
   //Roda o comando da instalação:  Instala as peças.//
   //
   Liga o servidor: python -m uvicorn main:app --reload