# Histórias de Usuário - IsoMix Studio
## Estruturadas por Camada BMAD

---

## 🏢 Business Layer (Valor & Acesso)

### US-B01: Gestão de Limites de Upload
**Como** usuário Free,  
**Quero** ser notificado se meu arquivo exceder o limite de tamanho ou tempo,  
**Para que** eu entenda as limitações do serviço antes de esperar pelo upload.

#### Critérios de Aceite
- [ ] Validar arquivo > 10MB ou > 5 minutos
- [ ] Exibir mensagem de erro amigável sugerindo upgrade ou corte do áudio
- [ ] Mostrar progresso de upload em tempo real
- [ ] Cancelar upload automaticamente se exceder limite

#### Prioridade: Alta
#### Estimativa: 3 pontos

---

### US-B02: Propriedade do Conteúdo
**Como** músico,  
**Quero** que meus arquivos processados sejam privados,  
**Para que** minhas composições não fiquem acessíveis publicamente.

#### Critérios de Aceite
- [ ] URLs de download devem ser assinadas (signed URLs) ou temporárias
- [ ] Implementar rotina de limpeza (garbage collection) de arquivos após 24h
- [ ] Associar arquivos estritamente ao UUID da sessão
- [ ] Logs de acesso para auditoria

#### Prioridade: Crítica
#### Estimativa: 5 pontos

---

### US-B03: Upgrade para Plano Pro
**Como** usuário Free que atingiu o limite diário,  
**Quero** ver uma oferta clara do Plano Pro,  
**Para que** eu possa decidir se vale a pena assinar.

#### Critérios de Aceite
- [ ] Modal de upgrade ao atingir limite de uploads
- [ ] Comparação visual Free vs Pro
- [ ] Integração com gateway de pagamento (Stripe)
- [ ] Ativação imediata após pagamento

#### Prioridade: Média
#### Estimativa: 8 pontos

---

## 🧠 Model Layer (Inteligência & Processamento)

### US-M01: Separação de Fontes (Inference)
**Como** sistema,  
**Devo** receber um arquivo de áudio bruto e executar o modelo de separação,  
**Para que** sejam gerados 4 arquivos de áudio distintos (stems) e salvos no storage.

#### Critérios de Aceite
- [ ] Input: 1 arquivo estéreo. Output: 4 arquivos (`vocal.wav`, `drums.wav`, `bass.wav`, `other.wav`)
- [ ] Tratamento de erro caso o áudio seja silêncio ou corrompido
- [ ] Processamento em worker assíncrono (Celery)
- [ ] Atualização de status em tempo real (PROCESSING → READY)

#### Prioridade: Crítica
#### Estimativa: 13 pontos

---

### US-M02: Normalização de Volume
**Como** sistema,  
**Devo** normalizar o volume das faixas separadas,  
**Para que** o som não fique distorcido ou muito baixo quando carregado no mixer.

#### Critérios de Aceite
- [ ] Aplicar normalização peak a -1dB em cada stem
- [ ] Preservar dinâmica original (não usar compressão excessiva)
- [ ] Validar que nenhum stem tenha clipping
- [ ] Logs de nível de volume pré e pós-normalização

#### Prioridade: Alta
#### Estimativa: 5 pontos

---

### US-M03: Suporte a Múltiplos Modelos
**Como** administrador,  
**Quero** poder escolher entre Demucs e Spleeter,  
**Para que** eu possa balancear qualidade vs velocidade.

#### Critérios de Aceite
- [ ] Variável de ambiente `AI_MODEL=demucs|spleeter`
- [ ] Fallback automático se modelo primário falhar
- [ ] Métricas de tempo de processamento por modelo
- [ ] Documentação de trade-offs

#### Prioridade: Baixa
#### Estimativa: 8 pontos

---

## 🖥️ Application Layer (Interface & Interação)

### US-A01: Controle de Mixer (Faders)
**Como** usuário no dashboard,  
**Quero** ajustar o volume da bateria independentemente do vocal,  
**Para que** eu possa criar uma versão "drumless" para praticar.

#### Critérios de Aceite
- [ ] Movimentar o fader da bateria altera o volume apenas desse canal em tempo real
- [ ] O fader deve ter resposta visual imediata (< 50ms)
- [ ] Range de 0 a 100% com step de 1%
- [ ] Indicador numérico do volume atual

#### Prioridade: Crítica
#### Estimativa: 5 pontos

---

### US-A02: Funcionalidade Solo/Mute
**Como** produtor,  
**Quero** clicar no botão "S" (Solo) no canal de voz,  
**Para que** todos os outros instrumentos fiquem mudos instantaneamente para eu conferir a afinação.

#### Critérios de Aceite
- [ ] Ativar "Solo" em um canal muta todos os outros
- [ ] Ativar "Mute" em um canal silencia apenas ele
- [ ] Lógica visual: Botão Solo deve acender amarelo; Mute deve acender vermelho
- [ ] Múltiplos canais podem estar em Solo simultaneamente

#### Prioridade: Alta
#### Estimativa: 5 pontos

---

### US-A03: Download da Mixagem Personalizada
**Como** usuário,  
**Quero** baixar o áudio exatamente como estou ouvindo (ex: sem bateria e com vocal baixo),  
**Para que** eu possa levar esse arquivo para meu ensaio.

#### Critérios de Aceite
- [ ] O backend deve receber os parâmetros de volume/mute atuais do frontend
- [ ] O sistema deve usar ffmpeg (ou similar) para remixar os stems com esses parâmetros e entregar o arquivo final
- [ ] Formato de saída: MP3 (192kbps) para Free, WAV (44.1kHz) para Pro
- [ ] Tempo de renderização < 30 segundos para arquivo de 5 minutos

#### Prioridade: Crítica
#### Estimativa: 8 pontos

---

### US-A04: Visualização de Waveform
**Como** usuário,  
**Quero** ver a forma de onda (waveform) de cada faixa enquanto ela toca,  
**Para que** eu saiba quando um instrumento vai entrar ou sair.

#### Critérios de Aceite
- [ ] Waveform renderizado usando Wavesurfer.js
- [ ] Cursor de reprodução sincronizado com o áudio
- [ ] Zoom in/out na timeline
- [ ] Cores distintas para cada canal (Vocal=azul, Drums=vermelho, etc.)

#### Prioridade: Média
#### Estimativa: 8 pontos

---

### US-A05: Controle de Pan (L/R)
**Como** usuário avançado,  
**Quero** ajustar o panorama (esquerda/direita) de cada canal,  
**Para que** eu possa criar uma mixagem espacial personalizada.

#### Critérios de Aceite
- [ ] Knob rotativo de Pan (-100% L a +100% R)
- [ ] Centro (0%) como posição padrão
- [ ] Aplicação em tempo real via Web Audio API
- [ ] Indicador visual da posição atual

#### Prioridade: Baixa
#### Estimativa: 5 pontos

---

### US-A06: Player Global Sincronizado
**Como** usuário,  
**Quero** que todas as faixas toquem perfeitamente sincronizadas,  
**Para que** a experiência seja profissional.

#### Critérios de Aceite
- [ ] Latência de sincronização < 10ms entre canais
- [ ] Controles: Play, Pause, Stop, Seek
- [ ] Barra de progresso interativa
- [ ] Exibição de tempo atual e total (mm:ss)

#### Prioridade: Crítica
#### Estimativa: 13 pontos

---

## 📦 Domain Layer (Regras & Dados)

### US-D01: Criação de Sessão de Projeto
**Como** sistema,  
**Devo** criar um ID único para cada upload realizado,  
**Para que** os 4 stems gerados sejam agrupados logicamente em uma entidade "Projeto".

#### Critérios de Aceite
- [ ] Entidade `Project` criada no banco de dados com status `PROCESSING` → `READY`
- [ ] Relacionamento 1:N entre `Project` e `Stem`
- [ ] UUID v4 como identificador único
- [ ] Timestamp de criação e expiração

#### Prioridade: Crítica
#### Estimativa: 5 pontos

---

### US-D02: Validação de Formato de Áudio
**Como** sistema,  
**Devo** verificar o MIME type real do arquivo (não apenas a extensão),  
**Para que** eu garanta que o processador de IA receba apenas dados de áudio válidos.

#### Critérios de Aceite
- [ ] Rejeitar arquivos que são renomeados incorretamente (ex: `.exe` renomeado para `.mp3`)
- [ ] Suportar MP3, WAV, OGG e FLAC
- [ ] Validar header do arquivo (magic bytes)
- [ ] Mensagem de erro específica para formato inválido

#### Prioridade: Alta
#### Estimativa: 3 pontos

---

### US-D03: Persistência de Metadados
**Como** sistema,  
**Devo** salvar metadados do arquivo original (duração, bitrate, sample rate),  
**Para que** eu possa exibir informações técnicas ao usuário.

#### Critérios de Aceite
- [ ] Extrair metadados usando `ffprobe` ou `mutagen`
- [ ] Armazenar: duração, bitrate, sample_rate, channels
- [ ] Exibir no dashboard do mixer
- [ ] Usar para validação de limites (Free vs Pro)

#### Prioridade: Média
#### Estimativa: 3 pontos

---

### US-D04: Garbage Collection de Arquivos
**Como** sistema,  
**Devo** deletar automaticamente arquivos processados após 24 horas,  
**Para que** o storage não fique sobrecarregado.

#### Critérios de Aceite
- [ ] Cron job executado a cada 1 hora
- [ ] Deletar projetos com `created_at` > 24h
- [ ] Deletar arquivos do storage (S3/MinIO)
- [ ] Logs de arquivos deletados para auditoria

#### Prioridade: Alta
#### Estimativa: 5 pontos

---

### US-D05: Histórico de Projetos (Pro)
**Como** usuário Pro,  
**Quero** acessar meus projetos anteriores por 30 dias,  
**Para que** eu possa continuar uma mixagem que comecei ontem.

#### Critérios de Aceite
- [ ] Lista de projetos ordenada por data (mais recente primeiro)
- [ ] Thumbnail da waveform como preview
- [ ] Botão "Abrir no Mixer"
- [ ] Expiração estendida para 30 dias (apenas Pro)

#### Prioridade: Baixa
#### Estimativa: 8 pontos

---

## 📊 Resumo de Priorização

| Camada | Críticas | Altas | Médias | Baixas | Total |
|--------|----------|-------|--------|--------|-------|
| Business | 1 | 0 | 1 | 0 | 2 |
| Model | 1 | 1 | 0 | 1 | 3 |
| Application | 3 | 1 | 2 | 1 | 7 |
| Domain | 1 | 2 | 1 | 1 | 5 |
| **TOTAL** | **6** | **4** | **4** | **3** | **17** |

---

## 🎯 Sprint 1 - MVP (Histórias Críticas)
1. US-M01: Separação de Fontes
2. US-A01: Controle de Mixer (Faders)
3. US-A03: Download da Mixagem
4. US-A06: Player Global Sincronizado
5. US-D01: Criação de Sessão de Projeto
6. US-B02: Propriedade do Conteúdo

**Total: 49 pontos**

---

## 📝 Notas de Implementação

### Dependências Técnicas
- **US-A06** depende de **US-M01** (precisa dos stems para tocar)
- **US-A03** depende de **US-A01** e **US-A02** (precisa dos parâmetros do mixer)
- **US-D05** depende de **US-D01** (precisa da entidade Project)

### Riscos Identificados
- ⚠️ Sincronização de áudio multicanal pode ser complexa (US-A06)
- ⚠️ Tempo de processamento da IA pode frustrar usuários (US-M01)
- ⚠️ Custos de storage podem escalar rapidamente (US-D04)

### Próximos Passos
1. Validar histórias com stakeholders
2. Criar protótipo de interface do mixer
3. Benchmark de modelos de IA (Demucs vs Spleeter)
4. Definir infraestrutura de deployment
