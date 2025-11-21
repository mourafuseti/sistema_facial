
## Instruções do Copilot / Agente de IA para este repositório

Objetivo
- Orientações curtas e práticas para que um agente de IA possa ser produtivo rapidamente neste repositório.

Fatos rápidos (o que encontramos)
- Este repositório contém atualmente três pastas no nível superior: `faces_autorizadas/`, `capturas_nao_autorizadas/` e `lista_negra_faces/` (todas vazias no momento da análise).
- Não foram encontrados arquivos de código, manifests (por exemplo, `package.json`, `requirements.txt`, `pyproject.toml`, `README.md`) nem configuração de CI na raiz do repositório.

Do que este repositório parece tratar
- Pelos nomes das pastas (em português):
  - `faces_autorizadas/` — armazenamento de imagens ou dados de indivíduos autorizados.
  - `capturas_nao_autorizadas/` — imagens capturadas ou eventos de pessoas não autorizadas.
  - `lista_negra_faces/` — lista negra de faces (imagens ou metadados).

Objetivos principais para um agente de IA (tarefas concretas e encontráveis)
1. Preservar a estrutura de diretórios. Não mover ou apagar as três pastas do nível superior, exceto se for instruído a fazê-lo.
2. Ao adicionar código, coloque-o sob um diretório de nível superior `src/` (preferido) ou `app/` e adicione um `README.md` mínimo explicando como executar.
3. Se adicionar dependências de tempo de execução, inclua também um manifesto de dependências (`requirements.txt` para Python ou `package.json` para Node). Documente os comandos para criar um virtualenv / instalar dependências no `README`.

Convenções específicas do repositório (derivadas do que existe)
- Trate as três pastas como buckets de dados. Mantenha arquivos de imagem e quaisquer metadados por imagem lado a lado (mesmo nome-base). Exemplo: `faces_autorizadas/joao_silva_01.jpg` e `faces_autorizadas/joao_silva_01.json`.
- Use nomes de arquivo em UTF-8 e evite caracteres de caminho que possam diferir entre sistemas operacionais (prefira nomes simples e ASCII quando possível).

Como proceder ao adicionar funcionalidades ou testes
- Adicione um script de entrada pequeno (`src/main.py` ou `src/index.js`) e inclua um `README.md` curto com exemplos de execução.
- Adicione um teste unitário/integrado pequeno que demonstre o fluxo pretendido (por exemplo, carregar uma imagem de `faces_autorizadas/` e calcular um hash/descritor). Coloque testes em `tests/` e inclua o comando do runner no `README`.

Integrações e dependências externas
- Nenhuma integração externa foi detectada. Se integrar um modelo (OpenCV, face-recognition, dlib, arquivos de modelo ML), comite apenas o código carregador e inclua os arquivos de modelo no `.gitignore`, com instruções de como obtê-los.

Suposições feitas (explícitas)
- Consideramos que o repositório é de reconhecimento facial baseado nos nomes das pastas. Isso é uma suposição — confirme com o dono do repositório antes de mudanças maiores.
- Não foi detectada uma linguagem de execução; as recomendações abaixo usam Python como padrão comum para tarefas de visão. Se o projeto usar outra linguagem, ajuste conforme necessário.

Quando estiver bloqueado (o que perguntar ao dono)
- Onde fica o ponto de entrada (script ou serviço) e qual o runtime preferido (Python, Node, etc.)?
- As imagens são apenas arquivos JPG/PNG ou existe também uma camada de metadados (JSON/BD)?
- Existem restrições de nomenclatura ou privacidade (regras sobre PII)?

Se atualizar ou criar este arquivo novamente
- Faça merge inteligente: preserve comandos de execução e workflows de CI escritos por humanos. Se existir uma versão mais recente do arquivo, extraia os passos de execução e caminhos de arquivo e mantenha-os.

Contato
- Em caso de dúvida, adicione um curto `TODO: esclarecer runtime e ponto de entrada` no `README.md` na raiz do repositório e peça esclarecimentos ao dono.

---
Se algo importante ficou de fora (ponto de entrada, linguagem, runner de testes), me informe e eu atualizo o documento.
