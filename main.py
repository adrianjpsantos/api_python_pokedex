from fastapi import FastAPI
from mysql import connector

app = FastAPI()


db = connector.connect(
    host="localhost", user="adrianjose", password="123456", database="pokedex"
)


@app.get("/")
def init():
    return {"message": "API RUNNING"}


@app.get("/genders")
def all_genders():
    query = db.cursor(dictionary=True)
    query.execute("SELECT Id,Name FROM gender")
    response = query.fetchall()

    if response:
        return {"code": "200", "status": "SUCCESS", "genders": response}
    else:
        return {"code": "404", "status": "ERROR", "genders": "Sem Genêros"}


@app.get("/generations")
def all_generations():
    query = db.cursor(dictionary=True)
    query.execute("SELECT Id,Name FROM generation")
    response = query.fetchall()

    if response:
        return {"code": "200", "status": "SUCCESS", "generations": response}
    else:
        return {"code": "404", "status": "ERROR", "generations": "Sem Gerações"}


@app.get("/types")
def all_types():
    query = db.cursor(dictionary=True)
    query.execute("SELECT Id,Name FROM types")
    response = query.fetchall()

    if response:
        return {"code": "200", "status": "SUCCESS", "types": response}
    else:
        return {"code": "404", "status": "ERROR", "types": "Sem Tipos"}


@app.get("/pokemons")
def all_pokemons():
    query = db.cursor(dictionary=True)
    query.execute("SELECT p.Number,p.Name FROM pokemons as p ORDER BY number")
    response = query.fetchall()
    result = response

    if result:
        return {"code": "200", "status": "SUCCESS", "pokemons": result}
    else:
        return {"code": "404", "status": "ERROR", "pokemons": "Sem Pokemons"}


@app.get("/pokemon")
def pokemon():
    return {
        "code": "777",
        "status": "ERROR",
        "Message": "Faltam parametros nesta requisição",
    }


@app.get("/pokemon/{number}")
def pokemon(
    number: int,
    evolvedfrom: bool = False,
    ability: bool = False,
    type: bool = False,
    weaknesses: bool = False,
):
    # GET POKEMON
    query = db.cursor(dictionary=True)
    query.execute(
        f"SELECT p.Number,p.Name,p.Description,g.Name as Gender,gene.Name as Generation,p.EvolvedFrom FROM pokemons as p INNER JOIN gender AS g INNER JOIN generation as gene ON p.genderId = g.Id AND p.generationId = gene.Id  WHERE p.number = {number}"
    )
    response = query.fetchmany(size=1)

    if not response:
        return {"code": "777", "status": "ERROR", "Message": "Este Pokemon não existe"}
    pokemon = response[0]

    # GET ABILITIES FROM POKEMON
    if ability:
        query.execute(
            f"SELECT a.Name FROM abilities as a INNER JOIN pokemonabilities as pa ON a.Id = pa.AbilityId WHERE pa.PokemonNumber = {number}"
        )
        response = query.fetchall()
        if response:
            pokemon["Abilities"] = response

    # GET TYPES FROM POKEMON
    if type:
        query.execute(
            f"SELECT t.Id,t.Name FROM types as t INNER JOIN pokemontypes as pt ON t.Id = pt.TypeId WHERE pt.PokemonNumber = {number}"
        )
        response = query.fetchall()
        if response:
            pokemon["Types"] = response

    # GET WEAKNESSES TYPES FROM POKEMON
    if weaknesses:
        query.execute(
            f"SELECT t.Id,t.Name FROM types as t INNER JOIN weaknesses as w ON t.Id = w.TypeId WHERE w.PokemonNumber = {number}"
        )
        response = query.fetchall()
        if response:
            pokemon["Weaknesses"] = response

    # GET EVOLVED FROM POKEMON
    efNumber = pokemon["EvolvedFrom"]
    if efNumber and evolvedfrom:
        query.execute(
            f"SELECT p.Number,p.Name FROM pokemons as p WHERE p.number = {efNumber}"
        )
        response = query.fetchmany(size=1)
        if not response:
            return {
                "code": "777",
                "status": "ERROR",
                "Message": "EvolvedFrom : Falha ao achar o pokemon",
            }
        pokemon["EvolvedFrom"] = response[0]
    else:
        pokemon.pop("EvolvedFrom")
    # RETURN POKEMON
    if pokemon:
        return {"code": "200", "status": "SUCCESS", "pokemon": pokemon}


# GET WEAKNESSES TYPE FROM POKEMON
@app.get("/pokemon/{pokemonNumber}/weaknesses")
def get_weaknesses(pokemonNumber: int):
    # GET WEAKNESSES TYPES FROM POKEMON
    if pokemonNumber:
        query = db.cursor(dictionary=True)
        query.execute(
            f"SELECT t.Id,t.Name FROM types as t INNER JOIN weaknesses as w ON t.Id = w.TypeId WHERE w.PokemonNumber = {pokemonNumber}"
        )
        response = query.fetchall()
        if response:
            return {
                "code": "200",
                "status": "SUCCESS",
                "PokemonId": pokemonNumber,
                "Weaknesses": response,
            }
        else:
            return {
                "code": "777",
                "status": "ERROR",
                "PokemonId": pokemonNumber,
                "Weaknesses": "Não Tem?",
            }


# GET TYPES FROM POKEMON
@app.get("/pokemon/{pokemonNumber}/types")
def get_types(pokemonNumber: int):
    if pokemonNumber:
        query = db.cursor(dictionary=True)
        query.execute(
            f"SELECT t.Id,t.Name FROM types as t INNER JOIN pokemontypes as pt ON t.Id = pt.TypeId WHERE pt.PokemonNumber = {pokemonNumber}"
        )
        response = query.fetchall()
        if response:
            return {
                "code": "200",
                "status": "SUCCESS",
                "PokemonId": pokemonNumber,
                "Types": response,
            }
        else:
            return {
                "code": "777",
                "status": "ERROR",
                "PokemonId": pokemonNumber,
                "Types": "Não Tem?",
            }


# GET GENERATION FROM POKEMON
@app.get("/pokemon/{pokemonNumber}/generation")
def get_types(pokemonNumber: int):
    query = db.cursor(dictionary=True)
    query.execute(
        f"SELECT g.Id,g.Name FROM generation as g INNER JOIN pokemons as p ON g.Id = p.GenerationId WHERE p.Number = {pokemonNumber} LIMIT 1"
    )
    response = query.fetchmany(size=1)
    if response:
        return {
            "code": "200",
            "status": "SUCCESS",
            "PokemonId": pokemonNumber,
            "Generation": response,
        }
    else:
        return {
            "code": "777",
            "status": "ERROR",
            "PokemonId": pokemonNumber,
            "Generation": "Não Tem?",
        }

# GET GENDER FROM POKEMON
@app.get("/pokemon/{pokemonNumber}/gender")
def get_types(pokemonNumber: int):
    query = db.cursor(dictionary=True)
    query.execute(
        f"SELECT g.Id,g.Name FROM gender as g INNER JOIN pokemons as p ON g.Id = p.GenderId WHERE p.Number = {pokemonNumber}"
    )
    response = query.fetchmany(size=1)
    if response:
        return {
            "code": "200",
            "status": "SUCCESS",
            "PokemonId": pokemonNumber,
            "Generation": response,
        }
    else:
        return {
            "code": "777",
            "status": "ERROR",
            "PokemonId": pokemonNumber,
            "Generation": "Não Tem?",
        }
