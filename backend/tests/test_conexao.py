from src.database.database import users
print("Conexao funcionando!")

print("Quantidade de usuarios:", users.count_documents({}))