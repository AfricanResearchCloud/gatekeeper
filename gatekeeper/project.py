class Project(dict):
    def __init__(self, project):
        self['name'] = project.name
        self['id'] = project.id
        self['description'] = project.description
        self['researchField'] = project.researchField if hasattr(project, 'researchField') else None
        self['primaryInstitution'] = project.primaryInstitution if hasattr(project, 'primaryInstitution') else None
