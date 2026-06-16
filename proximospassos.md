## Implementação de Logout e Sair do Sistema

Atualmente existe apenas o botão:

[Sair do Sistema]

Gostaria de separar as funcionalidades em dois botões.

----------------------------------------

Botão 1: Logout

Função:
- Encerrar a sessão do usuário atual;
- Fechar o Menu Principal;
- Fechar as janelas abertas da sessão atual;
- Limpar os dados do usuário logado;
- Retornar automaticamente para a tela de Login.

Fluxo:

Login
↓
Menu Principal
↓
Logout
↓
Tela de Login

Objetivo:
Permitir troca rápida de usuário sem fechar o sistema.

----------------------------------------

Botão 2: Sair do Sistema

Função:
- Encerrar completamente a aplicação;
- Fechar todas as janelas;
- Finalizar o programa.

Fluxo:

Login
↓
Menu Principal
↓
Sair do Sistema
↓
Programa encerrado

----------------------------------------

Layout

Adicionar os dois botões no Menu Principal:

[ Logout ]   [ Sair do Sistema ]

Sugestão de cores:

Logout:
Azul ou Amarelo

Sair do Sistema:
Vermelho

----------------------------------------

Confirmações

Logout:

"Deseja encerrar a sessão atual?"

[Sim] [Não]

Sair do Sistema:

"Deseja realmente fechar o sistema?"

[Sim] [Não]

----------------------------------------

Importante

Após o Logout:
- Não fechar a aplicação;
- Abrir novamente a tela de Login;
- Permitir que outro perfil faça login imediatamente.