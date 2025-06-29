# from app.Config.database import get_db_connection

# def descobrir_interface():
#     db = get_db_connection()
    
#     print("Tipo do objeto:", type(db))
#     print("Métodos disponíveis:")
    
#     # Listando métodos disponíveis
#     for metodo in dir(db):
#         if not metodo.startswith('_'):
#             print(f"  - {metodo}")
    
#     db.close()

# descobrir_interface()



from app.Config.database import get_db_connection
import os

# def teste_update_um():
#     db = get_db_connection()
#     conn = db.connection
#     cursor = conn.cursor()
    
#     try:
#         caminho = "/Users/joaopacheco/Downloads/devotionals/devocional_1_completo.mp3"
        
#         if os.path.exists(caminho):
#             with open(caminho, 'rb') as f:
#                 dados_audio = f.read()
            
#             # UPDATE apenas no devocional ID 1
#             cursor.execute("""
#                 UPDATE devotionals_flow 
#                 SET pt_br_masculino = %s 
#                 WHERE id = 1
#             """, (dados_audio,))
            
#             if cursor.rowcount > 0:
#                 conn.commit()
#                 print("✅ Teste UPDATE funcionou! Devocional ID 1 atualizado.")
#             else:
#                 print("⚠️ Nenhum devocional com ID 1 encontrado")
#         else:
#             print("❌ Arquivo devocional_1_completo.mp3 não encontrado")
        
#     except Exception as e:
#         print(f"❌ Erro no teste: {e}")
#         conn.rollback()
    
#     finally:
#         cursor.close()
#         db.close()

# # Verificar status atual
# def verificar_status():
#     db = get_db_connection()
#     conn = db.connection
#     cursor = conn.cursor()
    
#     try:
#         # Total de devocionais
#         cursor.execute("SELECT COUNT(*) FROM devotionals_flow")
#         total = cursor.fetchone()[0]
        
#         # Quantos têm áudio
#         cursor.execute("SELECT COUNT(*) FROM devotionals_flow WHERE pt_br_masculino IS NOT NULL")
#         com_audio = cursor.fetchone()[0]
        
#         # Sem áudio
#         sem_audio = total - com_audio
        
#         print(f"📊 Status dos devocionais:")
#         print(f"  Total: {total}")
#         print(f"  Com áudio: {com_audio}")
#         print(f"  Sem áudio: {sem_audio}")
        
#     except Exception as e:
#         print(f"❌ Erro: {e}")
    
#     finally:
#         cursor.close()
#         db.close()

# if __name__ == "__main__":
#     # Primeiro, vamos ver o status
#     verificar_status()
    
#     # Teste com 1 devocional
#     teste_update_um()
    
#     # Se funcionar, execute todos:
#     # atualizar_audios_existentes()





def atualizar_audios_com_logs():
    print("🚀 Iniciando processo de atualização...")
    
    db = get_db_connection()
    conn = db.connection
    cursor = conn.cursor()
    
    pasta_audios = "/Users/joaopacheco/Downloads/devotionals/"
    print(f"📁 Pasta de áudios: {pasta_audios}")
    
    # Verificar se a pasta existe
    if not os.path.exists(pasta_audios):
        print(f"❌ Pasta não encontrada: {pasta_audios}")
        return
    
    atualizados = 0
    erros = 0
    nao_encontrados = 0
    
    try:
        # Começar com apenas 10 arquivos para teste
        print("🔄 Processando arquivos de 1 a 10...")
        
        for numero in range(12):  # Teste com apenas 10 primeiro
            print(f"\n📋 Processando devocional {numero}...")
            
            nome_arquivo = f"devocional_{numero}_completo.mp3"
            caminho_completo = os.path.join(pasta_audios, nome_arquivo)
            
            print(f"🔍 Procurando arquivo: {nome_arquivo}")
            
            if os.path.exists(caminho_completo):
                print(f"✅ Arquivo encontrado!")
                
                try:
                    # Verificar tamanho do arquivo
                    tamanho_arquivo = os.path.getsize(caminho_completo)
                    print(f"📏 Tamanho do arquivo: {tamanho_arquivo/1024:.1f}KB")
                    
                    # Ler arquivo
                    print(f"📖 Lendo arquivo...")
                    with open(caminho_completo, 'rb') as f:
                        dados_audio = f.read()
                    
                    print(f"✅ Arquivo lido com sucesso! {len(dados_audio)} bytes")
                    
                    # Verificar se o devocional existe
                    print(f"🔍 Verificando se devocional ID {numero} existe...")
                    cursor.execute("SELECT id FROM devotionals_flow WHERE id = %s", (numero,))
                    exists = cursor.fetchone()
                    
                    if not exists:
                        print(f"⚠️ Devocional ID {numero} não existe na tabela")
                        continue
                    
                    print(f"✅ Devocional ID {numero} existe!")
                    
                    # UPDATE
                    print(f"🔄 Executando UPDATE...")
                    cursor.execute("""
                        UPDATE devotionals_flow 
                        SET pt_br_masculino = %s 
                        WHERE id = %s
                    """, (dados_audio, numero))
                    
                    if cursor.rowcount > 0:
                        atualizados += 1
                        print(f"✅ Devocional ID {numero} ATUALIZADO com sucesso!")
                        
                        # Commit imediatamente
                        conn.commit()
                        print(f"💾 Commit realizado para devocional {numero}")
                    else:
                        print(f"⚠️ Nenhuma linha foi atualizada para ID {numero}")
                        
                except Exception as e:
                    erros += 1
                    print(f"❌ ERRO com arquivo {numero}: {e}")
                    conn.rollback()
                    continue
            else:
                nao_encontrados += 1
                print(f"❌ Arquivo NÃO encontrado: {nome_arquivo}")
        
        print(f"\n🏁 Processo finalizado!")
        print(f"✅ Atualizados: {atualizados}")
        print(f"❌ Erros: {erros}")
        print(f"📁 Não encontrados: {nao_encontrados}")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        conn.rollback()
    
    finally:
        cursor.close()
        db.close()
        print("🔒 Conexão fechada")

# Verificar arquivos na pasta
def listar_arquivos():
    pasta = "/Users/joaopacheco/Downloads/devotionals/"
    print(f"📁 Listando arquivos em: {pasta}")
    
    if os.path.exists(pasta):
        arquivos = [f for f in os.listdir(pasta) if f.endswith('.mp3')]
        print(f"🎵 Encontrados {len(arquivos)} arquivos MP3:")
        
        # Mostrar apenas os primeiros 10
        for arquivo in sorted(arquivos)[:10]:
            print(f"  - {arquivo}")
        
        if len(arquivos) > 10:
            print(f"  ... e mais {len(arquivos) - 10} arquivos")
    else:
        print("❌ Pasta não encontrada!")

if __name__ == "__main__":
    # Primeiro listar arquivos
    listar_arquivos()
    
    print("\n" + "="*50)
    
    # Depois executar update
    atualizar_audios_com_logs()



