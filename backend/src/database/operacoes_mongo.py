"""
+---------------------------------+
|                                 |
|   CUIDADO AO EXECUTAR ESSAS     |
|           OPERACOES             |
|                                 |
+---------------------------------+
"""

# executar sem mudar retornar erro usuario nao definido, ta bom!
# ctrl+d e troque UsUarios por users
# somente para teste a fim de estudos

ana = usuarios.find_one({
    "codigo": "A"
})

print(ana)

usuarios.update_one(
    {"codigo": "A"},
    {"$set": {"nome": "Ana Silva"}}
)

usuarios.update_one(
    {"codigo": "A"},
    {"$set": {"ativo": False}}
)

usuarios.delete_one({
    "codigo": "A"
})