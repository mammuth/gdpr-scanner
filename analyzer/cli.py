import logging
import os

import click

from analyzer.analyze import Analyzer


@click.group()
def cli():
    pass


@click.command()
@click.option('--debug', default=False, help='enable debug log verbosity', is_flag=True)
@click.option('--crawler-json', default='../output/crawler.json', help='filepath to crawler.json')
@click.option('--skip-write', default=False, help='skip writing the results to file', is_flag=True)
def analyze(debug, crawler_json, skip_write):
    """ This command analyzes the output of the crawler component. """
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s %(levelname)s\t%(name)s\t%(message)s',
        # filename='app.log',
        # filemode='w',
    )

    # Start analyzer
    main_dir = os.path.dirname(os.path.realpath(__file__))
    analyzer = Analyzer(crawler_metadata_filepath=os.path.join(main_dir, crawler_json))
    analyzer.run()

    if not skip_write:
        analyzer.write_results_to_file()


cli.add_command(analyze)
