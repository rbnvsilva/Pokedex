import logging
import os
import json

import azure.functions as func
from azure.data.tables import TableServiceClient
from azure.core.exceptions import ResourceNotFoundError
from schema import Schema, And


def main(req: func.HttpRequest) -> func.HttpResponse:

    pokemonName = req.route_params.get('pokemonName')

    input = {
        u'pokemonName': pokemonName,
    }

    schema = Schema({
        'pokemonName': And(str, len)
    })

    if not schema.is_valid(input):
        return func.HttpResponse("Invalid pokemon name.", status_code=400)

    table_service_client = TableServiceClient.from_connection_string(
        conn_str=os.environ["AzureWebJobsStorage"])
    table_client = table_service_client.get_table_client(table_name="Pokedex")

    try:
        entityToUpdate = table_client.get_entity(pokemonName, pokemonName)
        table_client.delete_entity(pokemonName, pokemonName)
        input["pokedexNumber"] = entityToUpdate["PokedexNumber"]
        input["pokemonType"] = entityToUpdate["PokemonType"]
        input["pokemonColor"] = entityToUpdate["PokemonColor"]
        input["pokemonAttacks"] = entityToUpdate['PokemonAttacks'] if 'PokemonAttacks' in entityToUpdate else []
        return func.HttpResponse(json.dumps(input))
    except ResourceNotFoundError as ex:
        logging.exception(ex)
        return func.HttpResponse("That pokemon doesn't exist.", status_code=404)


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
            "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
            status_code=200
        )
