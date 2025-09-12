import click

import asyncio
from smartconnect import AsyncSmartClient

@click.group(help="A group of commands for getting data from a SMART Connect Server")
def cli():
    pass

common_options = [
    click.option('--url', help='SmartConnect URL', required=True),
    click.option('--username', help='SmartConnect username', required=True),
    click.option('--password', help='SmartConnect password', required=True),
]

def add_options(options):
    def _add_options(func):
        for option in reversed(options):
            func = option(func)
        return func
    return _add_options

@cli.command(help="Fetch the API Information for the SMART Connect Server")
@add_options(common_options)
def api_info(url, username, password):

    async def fn(client):
        val = await client.get_server_api_info()
        return val

    client = AsyncSmartClient(api=url, username=username, password=password)
    results = asyncio.run(fn(client))
    print(results)

@cli.command(help="List the Conservation Areas")
@add_options(common_options)
@click.option('--verbose', '-v', help='Verbose output', is_flag=True)
def conservation_areas(url, username, password, verbose):

    async def fn(client):
        val = await client.get_conservation_areas()

        if not val:
            print('no conservation areas found')
        return val
    


    client = AsyncSmartClient(api=url, username=username, password=password)
    results = asyncio.run(fn(client))
    for ca in results:
        print(ca) if verbose else print(f'{ca.uuid} - {ca.label}')

@cli.command(help="Download a Conservation Area Data Model")
@add_options(common_options)
@click.option('--ca_uuid', help='Conservation Area UUID', required=True)
@click.option('--filename', help='Output filename', required=True)
def download_datamodel(url, username, password, ca_uuid, filename):

    async def fn(client):
        val = await client.download_datamodel(ca_uuid=ca_uuid)
        return val

    client = AsyncSmartClient(api=url, username=username, password=password)
    results = asyncio.run(fn(client))
    results.save(filename=filename)

@cli.command(help="Post an Incident")
@add_options(common_options)
@click.option('--ca_uuid', help='Conservation Area UUID', required=True)
def post_incident(url, username, password, ca_uuid):

    payload = {
        "type": "Feature",
        "geometry": {
            "coordinates": [
                -88.99201666666667,
                17.299483333333335
            ]
        },
        "properties": {
            "dateTime": "2024-03-21T18:00:00",
            "smartDataType": "incident",
            "smartFeatureType": "waypoint/new",
            "smartAttributes": {
                "observationGroups": [
                    {
                        "observations": [
                            {
                                "observationUuid": "9e9bf25f-f305-4bcd-9e9d-9adf5786ab71",
                                "category": "gfwgladalert",
                                "attributes": {
                                    "confidence": 1
                                }
                            }
                        ]
                    }
                ],
                "comment": "Report: GFW Integrated Deforestation Cluster (3 alerts)\nImported: 2024-04-17T13:00:19.233942-06:00",
                "attachments": []
            }
        }
    }

    async def fn(client):
        val = await client.post_smart_request(json=payload, ca_uuid=ca_uuid)
        return val

    client = AsyncSmartClient(api=url, username=username, password=password)
    results = asyncio.run(fn(client))
    print(results)


if __name__ == '__main__':
    cli()
