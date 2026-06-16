## Mostrar o erro real da exportação Excel

Problema:

Ao clicar em Excel aparece apenas:

"Erro"

Isso não permite identificar a causa.

Correção necessária:

Substituir o tratamento genérico por um que exiba a mensagem real da exceção.

Exemplo:

except Exception as e:
    messagebox.showerror(
        "Erro ao exportar Excel",
        str(e)
    )

Objetivo:

Exibir o erro completo para diagnóstico.

Exemplos:

- Arquivo em uso
- Caminho inválido
- Biblioteca não encontrada
- Erro de gravação
- Erro de permissão

Não exibir apenas "Erro".