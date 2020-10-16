from flask import Blueprint, render_template, abort

from CTFd.utils import config
from CTFd.utils.config.visibility import scores_visible
from CTFd.utils.decorators.visibility import check_score_visibility
from CTFd.utils.helpers import get_infos
from CTFd.utils.scores import get_standings
from CTFd.utils.user import is_admin
from CTFd.models import TeamFieldEntries, TeamFields, Teams, db

def load(app):
    multi_sb = Blueprint('multi_sb', __name__, template_folder='templates')

    @multi_sb.route('/scoreboard/<sb>', methods=['GET'])
    @check_score_visibility
    def multi_scoreboard(sb=None):
        if sb == None:
            sb = 'Global'
        infos = get_infos()
    
        if config.is_scoreboard_frozen():
            infos.append("Scoreboard has been frozen")
    
        if is_admin() is True and scores_visible() is False:
            infos.append("Scores are not currently visible to users")
    
        standings = get_standings()
        teams = []
        scoreboards = ["Global"]
        for t in Teams.query.all():
            if sb == "Global" and (t.name not in teams):
                teams.append(t.name)
            for f in t.fields:
                if f.name not in scoreboards:
                    scoreboards.append(f.name)
                if f.name == sb and (t.name not in teams):
                    teams.append(t.name)
    
        if sb not in scoreboards:
            abort(404)
    
        filtered_standings = [st for st in standings if st[2] in teams]
    
        return render_template("multi_scoreboard.html", standings=filtered_standings, infos=infos, scoreboards=scoreboards, scoreboard=sb)

    app.register_blueprint(multi_sb)
    app.view_functions['scoreboard.listing'] = multi_scoreboard
