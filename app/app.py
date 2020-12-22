#!/usr/bin/env python3

import codecs
import functools
import hmac
import os
import pathlib
import itertools

import flask
import sqlalchemy
import sqlalchemy.orm as orm
import sqlalchemy.sql as sql

from models import (
    Base, Nomination, Token, Vote
)

app = flask.Flask(
    __name__,
    static_folder=str(pathlib.Path(__file__).absolute().parent / "assets"),
    static_url_path="/assets"
)
app.config.from_mapping(os.environ)
db_engine = sqlalchemy.create_engine(app.config["SQLALCHEMY_URI"])
db_factory = orm.sessionmaker(bind=db_engine)
db = orm.scoped_session(db_factory)


@app.before_first_request
def create_tables():
    Base.metadata.create_all(db_engine)


@app.teardown_request
def remove_session(_=None):
    db.remove()


@app.route("/")
def index():
    return flask.render_template("index.html")


@app.route("/dashboard")
def dashboard():
    nominations = db.query(Nomination).order_by(Nomination.id).all()

    return flask.render_template("dashboard.html", nominations=nominations)


def issue_token(nid):
    token = (db.query(Token)
             .filter(Token.nomination_id == nid)
             .filter(Token.assigned == False)
             .with_for_update(skip_locked=True)
             .first())

    if token is None:
        return None

    token.assigned = True
    db.commit()

    return token.value


@app.route("/token/<int:nid>", methods=["POST"])
def rich_token(nid):
    token = issue_token(nid)
    return flask.render_template("token.html", token=token)


@app.route("/token/<int:nid>/plain")
def plain_token(nid):
    token = issue_token(nid)
    if token is None:
        return "No tokens remaining", 400

    return token


@app.route("/vote/<int:nid>", methods=["GET", "POST"])
def vote_nomination(nid):
    try:
        nomination = (db.query(Nomination)
                      .filter(Nomination.id == nid)
                      .one())
    except orm.exc.NoResultFound:
        return "No such nomination", 404

    if flask.request.method == "POST":
        try:
            token = (db.query(Token)
                        .filter(Token.value == flask.request.form["token"])
                        .one())
        except orm.exc.NoResultFound:
            return flask.render_template(
                "vote.html",
                nomination=nomination,
                error="Токен введён некорректно."
            )

        if token.nomination_id != nomination.id:
            return flask.render_template(
                "vote.html",
                nomination=nomination,
                error="Вы ввели токен неверной номинации."
            )

        action = flask.request.form.get("action")
        if action == "bulletin":
            votes = (db.query(Vote)
                     .filter(Vote.token_id == token.id)
                     .all())

            return flask.render_template(
                "vote.html",
                nomination=nomination,
                token=token,
                votes=votes
            )
        elif action == "vote":
            vote_data = []

            vote_range = list(range(1, len(nomination.nominees) + 1))
            for i in vote_range:
                try:
                    vote_data.append(int(flask.request.form[f"nominee-{i}"]))
                except:
                    return "vote: NaN", 400

            if set(vote_data) != set(vote_range):
                return flask.render_template(
                    "vote.html",
                    nomination=nomination,
                    token=token,
                    votes=votes,
                    error="Вы поставили одинаковые оценки двум номинантам, поставили некорректные "
                          "оценки или пропустили какое-то поле."
                )

            vote = Vote(token_id=token.id, data=vote_data)
            db.add(vote)
            db.commit()
            return flask.render_template(
                "success.html",
                nomination=nomination
            )

        return "Invalid action", 400

    return flask.render_template(
        "vote.html",
        nomination=nomination
    )


if __name__ == "__main__":
    app.run(port=53024, debug=False)
