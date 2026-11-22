# Roteiro do vídeo — gRPC (≤ 5 min)

| Tempo | O que mostrar | O que falar |
|---|---|---|
| 0:00–0:40 | Abrir `proto/armazem.proto` | RPC faz chamada remota parecer local. gRPC = HTTP/2 + Protocol Buffers. O `.proto` é o contrato neutro de linguagem; dele se geram stubs para ~12 linguagens → interoperabilidade. Mostrar os 4 `rpc`. |
| 0:40–1:10 | `./demo.sh` no terminal | 2 containers numa rede virtual: servidor e cliente. Distribuição lógica, não geográfica. |
| 1:10–2:00 | Saída: **unário** + metadata | 1→1. Metadata inicial e trailers. Mostrar `NOT_FOUND` e `UNAUTHENTICATED` (interceptor): status do gRPC ≠ HTTP. |
| 2:00–2:40 | **Server streaming** | Itens chegam com +0,4 s: o cliente processa sem esperar a lista inteira (HTTP/2 stream). |
| 2:40–3:20 | **Client streaming** | 4 produtos enviados em fluxo → 1 resumo (um deles inválido, rejeitado). Casos de uso: upload/telemetria. |
| 3:20–4:00 | **Bidirecional** | Ofertas e contrapropostas intercaladas em tempo real, mesma conexão, sem polling. |
| 4:00–4:30 | **Deadline** + log do servidor | Cliente impôs 1 s; servidor viu `is_active()==False` e abortou: previne trabalho inútil / falha em cascata. |
| 4:30–5:00 | Tabela gRPC × REST do README | Quando usar cada um; limite: navegador precisa de gRPC-Web. |
