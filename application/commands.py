import csv
import os
from contextlib import closing

import click
import requests
from flask.cli import with_appcontext


@click.command()
@with_appcontext
def load():

    from application.extensions import db
    from application.models import LocalAuthority

    la_url = 'https://raw.githubusercontent.com/communitiesuk/digital-land-collector/master/data/organisation.tsv'
    print('Loading', la_url)
    with closing(requests.get(la_url, stream=True)) as r:
        reader = csv.DictReader(r.iter_lines(decode_unicode=True), delimiter='\t')
        for row in reader:
            if row['organisation'].startswith('local-authority'):
                la = LocalAuthority(id=row['organisation'],
                                    name=row['name'])
                db.session.add(la)
                db.session.commit()


@click.command()
@with_appcontext
def load_viability():
    from application.extensions import db
    from application.models import PlanningApplication, ViabilityAssessment

    path = os.path.dirname(os.path.realpath(__file__))
    planning_csv = os.path.join(path, 'data', 'planning-application.csv')
    viability_csv = os.path.join(path, 'data', 'viability-assessment.csv')

    with open(planning_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not PlanningApplication.query.filter_by(reference=row['reference']).first():
                planning_row = {}
                for k, v in row.items():
                    if v:
                        planning_row[k] = v
                pa = PlanningApplication(**planning_row)
                db.session.add(pa)
                db.session.commit()
            else:
                print('Planning application', row['reference'], 'already loaded')

    with open(viability_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not ViabilityAssessment.query.filter_by(id=row['id']).first():
                viability_row = {}
                for k, v in row.items():
                    if v:
                        viability_row[k] = v
                va = ViabilityAssessment(**viability_row)
                db.session.add(va)
                db.session.commit()
            else:
                print('Viability assessment', row['id'], 'already loaded')