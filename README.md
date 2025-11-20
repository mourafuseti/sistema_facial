

# 🚪 Sistema de Controle de Acesso Facial (Face Access Control System)

## Criador

**LEONARDO DE MOURA FUSETI**

  * **GitHub:** [https://github.com/mourafuseti](https://github.com/mourafuseti)

-----

## 📝 Descrição do Projeto

Este é um sistema robusto para **Controle de Acesso Facial em Tempo Real** desenvolvido em Python. Ele utiliza **CustomTkinter** para uma interface gráfica moderna e estável, e **OpenCV/Face Recognition** para processamento de vídeo e identificação biométrica. O sistema gerencia listas de acesso e registra todos os eventos (autorizados, desconhecidos e lista negra) em um banco de dados **SQLite**.

### 🔑 Funcionalidades Principais

  * **Reconhecimento Facial em Tempo Real:** Processamento de vídeo da webcam.
  * **Interface Gráfica (GUI):** Utiliza **CustomTkinter** para uma experiência de usuário limpa e responsiva.
  * **Multithreading:** O processamento pesado de reconhecimento facial é isolado em uma thread separada para evitar o travamento da interface.
  * **Gestão de Acesso:** Separação clara entre **Faces Autorizadas** e **Lista Negra**.
  * **Banco de Dados (SQLite):** Armazena data, hora, nome e status de cada evento de acesso.
  * **Captura Automática:** Salva automaticamente imagens de pessoas **Desconhecidas** e da **Lista Negra**.

-----

## 🛠️ Tecnologias Utilizadas

  * **Linguagem:** Python 3.x
  * **Visão Computacional:** `opencv-python`
  * **Reconhecimento Facial:** `face-recognition` (baseado em `dlib`)
  * **Interface Gráfica:** `customtkinter`
  * **Imagens:** `Pillow` (PIL)
  * **Banco de Dados:** `sqlite3` (nativo do Python)

-----

## ⚙️ Instalação e Configuração

Siga os passos abaixo para configurar e rodar o projeto em seu ambiente.

### 1\. Criar e Ativar Ambiente Virtual

É altamente recomendado usar um ambiente virtual para isolar as dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
.\venv\Scripts\activate   # Windows
```

### 2\. Instalar Dependências

O **`dlib`** (necessário para o `face-recognition`) pode exigir bibliotecas de desenvolvimento do sistema (`cmake`, etc.). Se tiver problemas, consulte a documentação do `dlib`.

```bash
pip install customtkinter opencv-python face-recognition Pillow numpy
```

### 3\. Estrutura de Pastas

O sistema criará automaticamente as pastas necessárias na primeira execução, mas você deve adicionar as imagens de faces. O código espera a seguinte estrutura:

```
seu_projeto_reconhecimento/
├── sistema_facial_gui_otimizado.py
├── controle_acesso.db  (Criado automaticamente)
├── faces_autorizadas/          <-- Coloque aqui as imagens das pessoas permitidas
│   └── nome_funcionario.jpg
├── lista_negra_faces/          <-- Coloque aqui as imagens das pessoas proibidas
│   └── nome_intruso.png
└── capturas_nao_autorizadas/   (Criado automaticamente)
```

**Importante:** Use arquivos `.jpg` ou `.png` e **nomeie o arquivo com o nome da pessoa** (ex: `joao_silva.jpg`).

-----

## ▶️ Como Rodar o Sistema

1.  Certifique-se de que sua **webcam** esteja conectada e disponível.
2.  Execute o script principal:

<!-- end list -->

```bash
python sistema_facial_gui_otimizado.py
```

3.  Na janela do CustomTkinter:
      * Clique em **📸 INICIAR CÂMERA**.
      * O feed de vídeo será exibido, e o reconhecimento começará em segundo plano.

-----

## 📚 Gerenciamento e Uso da GUI

### Cadastro de Faces

  * **Autorizados:** Adicione imagens à pasta `faces_autorizadas/`.
  * **Lista Negra:** Adicione imagens à pasta `lista_negra_faces/`.
  * As faces são carregadas automaticamente ao clicar em **INICIAR CÂMERA**.

### Visualização de Registros

  * Clique em **📜 Ver Registros** para abrir uma nova janela que exibe os últimos eventos registrados no banco de dados (`controle_acesso.db`).

### Indicadores Visuais em Tempo Real

| Status Detectado | Cor da Caixa | Ação do Sistema |
| :--- | :--- | :--- |
| **Autorizado** | Verde (Green) | Registra acesso no DB |
| **Lista Negra** | Vermelho (Red) | Registra alerta no DB e salva foto em `capturas_nao_autorizadas/` |
| **Desconhecido** | Laranja (Orange) | Registra alerta no DB e salva foto em `capturas_nao_autorizadas/` |

-----

## ⚠️ Solução de Problemas (Troubleshooting)

| Problema | Solução |
| :--- | :--- |
| **GUI Travando/Lenta** | O problema foi mitigado com multithreading e otimização. Se persistir, tente reduzir a resolução da sua webcam. |
| **Erro ao abrir Câmera** | Verifique se a webcam está sendo usada por outro aplicativo ou se o índice `cv2.VideoCapture(0)` está correto (tente `1` ou `2`). |
| **Erro na Instalação do dlib/face-recognition** | Certifique-se de que o `cmake` e as ferramentas de desenvolvimento do C++ estão instalados em seu sistema operacional antes de rodar o `pip install`. |
