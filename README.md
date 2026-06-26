# Sistema Loja de Carros

Sistema em Streamlit para ajudar uma loja de carros a controlar veiculos, fotos, clientes, propostas, vendas, despesas e lucro por carro.

## Funcoes da primeira versao

- Cadastro de veiculos com marca, modelo, ano, cor, km, placa, chassi, preco de compra, preco de venda e status.
- Status de veiculo: Disponivel, Reservado e Vendido.
- Cadastro de fotos por URL.
- Cadastro de clientes.
- Registro de propostas.
- Registro de vendas.
- Controle de despesas por veiculo.
- Relatorio de lucro por carro.
- Modo demo local quando o Supabase ainda nao esta configurado.
- Conexao com Supabase pela API REST, sem depender do pacote `supabase`.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configurar Supabase

1. Crie um projeto no Supabase.
2. Abra o SQL Editor.
3. Rode o conteudo do arquivo `supabase_schema.sql`.
4. Crie o arquivo `.streamlit/secrets.toml`.
5. Preencha:

```toml
SUPABASE_URL = "https://seu-projeto.supabase.co"
SUPABASE_ANON_KEY = "sua-chave-anon-publica"
```

## Subir para o GitHub

```bash
git init
git add .
git commit -m "Cria sistema da loja de carros"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/sistema-loja-carros.git
git push -u origin main
```

## Publicar

Use o Streamlit Community Cloud:

1. Conecte sua conta do GitHub.
2. Escolha o repositorio.
3. Configure o arquivo principal como `app.py`.
4. Adicione os secrets do Supabase no painel do Streamlit Cloud.

O app usa a API REST do Supabase com `requests`, evitando dependencias nativas que podem falhar em versoes novas do Python no Streamlit Cloud.

## Fotos dos carros

Nesta primeira versao, o campo de fotos aceita URLs, uma por linha. O proximo passo natural e usar o Supabase Storage para upload direto dos arquivos pelo Streamlit.

## Seguranca

As politicas do `supabase_schema.sql` estao abertas para facilitar o primeiro teste. Antes de usar com dados reais da loja, adicione login e troque as politicas por regras restritas.
