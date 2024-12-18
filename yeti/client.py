import yeti.api
import click


class Context:
    def __init__(self):
        self.client = None


pass_context = click.make_pass_decorator(Context, ensure=True)


@click.group()
@click.option("--api-key", envvar="YETI_API_KEY", required=True, help="Your API key.")
@click.option(
    "--endpoint", envvar="YETI_WEB_ROOT", required=True, help="The Yeti endpoint."
)
@pass_context  # Add this to pass the context to subcommands
def cli(ctx, api_key, endpoint):
    """
    Yeti python API client:
    """
    client = yeti.api.YetiApi(endpoint)
    client.auth_api_key(api_key)
    ctx.client = client


@cli.command()
@click.option("--name", required=False, default="")
@pass_context
def search_indicators(ctx, name):
    rules = ctx.client.search_indicators(name=name, indicator_type="yara")
    for rule in rules:
        print(rule["name"])


if __name__ == "__main__":
    cli()
