# PRD - IsoMix Studio
## Audio Source Separation WebApp

---

## 1. Visão Geral do Produto

O **IsoMix Studio** é uma plataforma SaaS que utiliza modelos de Deep Learning para realizar a **separação de fontes sonoras** (Source Separation) em arquivos de áudio. Diferente de conversores comuns, o IsoMix oferece uma interface de **Mesa de Som Digital (Mixer)** no navegador, permitindo ao usuário manipular volumes, isolar canais e exportar mixagens personalizadas em tempo real.

### Proposta de Valor
- **Democratizar a engenharia de áudio** para músicos amadores, produtores de conteúdo, DJs e entusiastas de karaokê
- **Interface visual intuitiva** simulando uma mesa de som profissional
- **Processamento de IA avançado** para separação de alta qualidade
- **Controle total** sobre cada elemento da música

---

## 2. Estrutura Arquitetural (BMAD)

Para garantir a escalabilidade e a separação de responsabilidades, o projeto segue a arquitetura BMAD:

| Camada | Responsabilidade | Componentes Chave |
|--------|------------------|-------------------|
| **Business** | Regras de monetização, gestão de cotas de usuário e perfis de uso (Free/Pro) | `UserProfile`, `SubscriptionHandler`, `UsageLimiter` |
| **Model** | Núcleo de IA responsável pela separação do áudio (Demucs/Spleeter) | `AudioSeparator`, `InferenceEngine`, `StemGenerator` |
| **Application** | Interface do usuário (Mixer), orquestração de upload/download e gerenciamento de estado da sessão | `MixerDashboard`, `AudioPlayerService`, `ExportManager` |
| **Domain** | Lógica central das entidades de áudio, validação de arquivos e persistência de metadados | `Track`, `Stem`, `ProjectSession`, `AudioFormatValidator` |

---

## 3. Requisitos Funcionais

### 3.1 Fluxo de Entrada (Upload & Model)
- ✅ O usuário deve poder fazer upload de arquivos de áudio (`.mp3`, `.wav`, `.flac`)
- ✅ O sistema deve processar o áudio utilizando um modelo de IA para separar em **4 faixas principais**:
  - **Vocals** (Voz)
  - **Drums** (Bateria)
  - **Bass** (Baixo)
  - **Other** (Outros instrumentos)
- ✅ O processamento deve ser **assíncrono** para não travar a interface

### 3.2 O Mixer (Application)
- ✅ Interface visual simulando uma **mesa de som** com 4 canais verticais
- ✅ **Controles por canal**:
  - Fader de Volume (0-100%)
  - Botão **Mute (M)**
  - Botão **Solo (S)**
  - Controle **Pan (L/R)**
- ✅ **Visualização de Waveform** sincronizada para cada faixa
- ✅ **Controle de transporte global**: Play, Pause, Seek e Loop

### 3.3 Exportação (Business/Domain)
- ✅ **Exportar Mix**: Renderizar um arquivo único (`.mp3`/`.wav`) combinando os volumes e ajustes atuais da mesa
- ✅ **Exportar Stems**: Baixar um arquivo `.zip` contendo as faixas separadas originais

---

## 4. Requisitos Não Funcionais

### Performance
- ⚡ **Latência do Player**: O áudio multicanal deve tocar em perfeita sincronia (< 10ms de desvio)
- ⚡ **Processamento da IA**: Deve ocorrer em background workers (ex: Celery/Redis) para não bloquear o servidor web

### Segurança
- 🔒 Arquivos processados devem ser associados estritamente à **sessão do usuário**
- 🔒 URLs de download devem ser **assinadas** (signed URLs) ou temporárias
- 🔒 Arquivos devem **expirar automaticamente** após X horas

### Escalabilidade
- 📈 Suporte a múltiplos usuários simultâneos através de **fila de processamento**
- 📈 Arquitetura preparada para **horizontal scaling** dos workers de IA

---

## 5. Público-Alvo

### Personas Principais

#### 🎸 Músico Amador
- **Necessidade**: Remover bateria para praticar com a música original
- **Uso**: Upload → Mute drums → Download

#### 🎤 Cantor de Karaokê
- **Necessidade**: Playback profissional sem voz principal
- **Uso**: Upload → Mute vocals → Download

#### 🎧 Produtor Musical
- **Necessidade**: Extrair samples específicos (ex: linha de baixo)
- **Uso**: Upload → Solo bass → Download stem individual

#### 🎵 DJ / Remixer
- **Necessidade**: Criar versões acapella ou instrumental
- **Uso**: Upload → Ajustar volumes → Exportar mix customizado

---

## 6. Diferencial Competitivo

| Concorrente | Limitação | IsoMix Studio |
|-------------|-----------|---------------|
| Lalal.ai | Apenas download de stems, sem mixer | ✅ Mixer interativo em tempo real |
| Moises.ai | Interface simples, sem controle fino | ✅ Controles profissionais (Pan, Solo, Mute) |
| Spleeter (CLI) | Requer conhecimento técnico | ✅ Interface web amigável |

---

## 7. Roadmap de Desenvolvimento

### Fase 1 - MVP (Mínimo Produto Viável)
- [ ] Upload de arquivos MP3/WAV
- [ ] Processamento com modelo Demucs (4 stems)
- [ ] Mixer básico com 4 canais (Volume + Mute)
- [ ] Exportação de mix final

### Fase 2 - Aprimoramentos
- [ ] Visualização de waveform
- [ ] Controles de Pan (L/R)
- [ ] Botão Solo
- [ ] Download de stems individuais

### Fase 3 - Profissionalização
- [ ] Efeitos (Reverb, EQ básico)
- [ ] Histórico de projetos
- [ ] Planos Free/Pro com limites de uso
- [ ] API para desenvolvedores

---

## 8. Métricas de Sucesso

### KPIs Principais
- **Taxa de Conversão**: % de uploads que resultam em download
- **Tempo Médio de Processamento**: < 60 segundos para arquivos de 5 minutos
- **NPS (Net Promoter Score)**: > 50
- **Retenção (D7)**: > 30% dos usuários retornam em 7 dias

### Métricas Técnicas
- **Uptime**: > 99.5%
- **Erro de Processamento**: < 2%
- **Latência de Sincronização**: < 10ms

---

## 9. Stack Tecnológica Recomendada

### Backend (Model + Domain)
- **Linguagem**: Python 3.11+
- **Framework**: FastAPI
- **IA**: Demucs (Meta) ou Spleeter (Deezer)
- **Queue**: Celery + Redis
- **Storage**: S3 (AWS) ou MinIO (self-hosted)

### Frontend (Application)
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Áudio**: Wavesurfer.js v7
- **UI**: Tailwind CSS + Radix UI
- **Estado**: Zustand

### Infraestrutura
- **Container**: Docker + Docker Compose
- **Reverse Proxy**: Nginx
- **Database**: PostgreSQL (metadados) + Redis (cache)

---

## 10. Considerações de Segurança

### Proteções Implementadas
- ✅ Validação de MIME type real (não apenas extensão)
- ✅ Limite de tamanho de arquivo (20MB free / 100MB pro)
- ✅ Rate limiting por IP e por usuário
- ✅ Sanitização de nomes de arquivo
- ✅ Isolamento de arquivos por sessão UUID
- ✅ Garbage collection automático (24h)

---

## 11. Monetização (Business Layer)

### Plano Free
- ✅ 5 uploads por dia
- ✅ Arquivos até 20MB (≈ 5 minutos)
- ✅ Qualidade standard (MP3 192kbps)
- ✅ Marca d'água no export

### Plano Pro ($9.99/mês)
- ✅ Uploads ilimitados
- ✅ Arquivos até 100MB (≈ 25 minutos)
- ✅ Qualidade premium (WAV 44.1kHz)
- ✅ Sem marca d'água
- ✅ Histórico de projetos (30 dias)

---

## Anexos

- [User Stories](./USER_STORIES.md)
- [Diagrama de Sequência](./SEQUENCE_DIAGRAM.md)
- [Arquitetura Técnica](./ARCHITECTURE.md)
