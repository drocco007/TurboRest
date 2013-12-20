# coding: utf-8
import cherrypy

from turbogears import expose
from turbogears.controllers import RootController, Controller


class RESTResource(Controller):
    @expose()
    def default(self, *vpath, **kw):
        http_method = cherrypy.request.method
        method = getattr(self, http_method)

        if not callable(method) or not getattr(method, 'exposed', False):
            raise cherrypy.HTTPError(405, '%s not allowed on %s' % (
                http_method, cherrypy.request.browser_url))

        return method(*vpath, **kw)


class CandidateApplicationsResource(RESTResource):
    def __init__(self, candidate_resource):
        self.candidate_resource = candidate_resource

    def __getattr__(self, attribute):
        try:
            # exercise for the reader...
            # return ApplicationResource(int(attribute))
            raise ValueError()
        except ValueError:
            super(CandidateApplicationsResource, self).__getattr__(attribute)

    @expose()
    def default(self):
        return {'success': True, 'applications': [{'application_id': 12345}],
                'candidate_id': self.candidate_resource.candidate_id}


class CandidateResource(RESTResource):
    def __init__(self, id):
        super(CandidateResource, self).__init__()
        self.candidate_id = id

        # in a real system, we'd
        # self.candidate = Candidate.get(id)

        # set up subordinate resources
        self.applications = CandidateApplicationsResource(self)

    @expose()
    def GET(self):
        return {'success': True, 'candidate': {'id': self.candidate_id}}

    @expose()
    def POST(self):
        return {'success': True}


# normally this would probably inherit from identity.SecureResource
class CandidateRootController(Controller):
    def __getattr__(self, attribute):
        try:
            return CandidateResource(int(attribute))
        except ValueError:
            super(CandidateRootController, self).__getattr__(attribute)

    @expose()
    def default(self):
        return 'candidate controller root<br/>' \
               '<a href="/">Back home</a>'


class Root(RootController):
    """The root controller of the application."""

    candidate = CandidateRootController()

    @expose()
    def index(self):
        return '<a href="/candidate">Candidate Controller</a><br/>' \
               '<a href="/candidate/1">Candidate 1 (GET)</a><br/>' \
               '<a href="/candidate/1/applications">Candidate 1 ' \
               'applications (GET)</a><br/>'